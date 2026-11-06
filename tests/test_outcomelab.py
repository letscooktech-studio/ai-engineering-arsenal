import contextlib
import io
import json
import socket
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Event, Thread
from unittest.mock import patch

from risk_lab.cli import main
from risk_lab.demo_http import demo_server
from risk_lab.http_verify import verify

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "http"


@contextlib.contextmanager
def serving(server):
    worker = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
    worker.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        worker.join()


class OutcomeLabTests(unittest.TestCase):
    def test_same_contract_rejects_broken_and_passes_fixed(self):
        for path in (EXAMPLES / "invoice-persistence.json", EXAMPLES / "webhook-idempotency.json"):
            receipts = []
            for variant, expected in (("broken", 1), ("fixed", 0)):
                with self.subTest(path=path.name, variant=variant):
                    with demo_server(variant) as server, serving(server) as url:
                        out = io.StringIO()
                        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                            code = main(["verify-http", "--contract", str(path), "--base-url", url,
                                         "--allow-local-writes", "--json"])
                        receipt = json.loads(out.getvalue())
                        print_line = (path.stem, variant, receipt["verdict"])
                        self.assertEqual(code, expected, print_line)
                        self.assertEqual(receipt["provenance"], "local-user-run")
                        self.assertEqual(receipt["verdict"], ("PASS", "FAIL")[expected])
                        receipts.append(receipt)
            self.assertEqual(len(receipts), 2)
            self.assertEqual(receipts[0]["contract_sha256"], receipts[1]["contract_sha256"])

    def test_invalid_target_or_missing_permission_makes_no_request(self):
        path = EXAMPLES / "webhook-idempotency.json"
        with demo_server("fixed") as server, serving(server) as url:
            self.assertEqual(verify(path, url, False)[1], 3)
            for target in ("http://localhost:8765", "https://127.0.0.1:8765", "http://example.com:8765",
                           "http://127.0.0.2:8765", "http://[::1]:8765", "file:///tmp/test",
                           "http://test@127.0.0.1:8765", url + "/", url + "?x", url + "#x"):
                with self.subTest(target=target):
                    self.assertEqual(verify(path, target, True)[1], 3)
            with patch.dict("os.environ", {"HTTP_PROXY": "http://127.0.0.1:1", "NO_PROXY": ""}):
                self.assertEqual(verify(path, url, True)[1], 0)

    def test_invalid_manifests(self):
        valid = (EXAMPLES / "webhook-idempotency.json").read_text()
        cases = [
            valid.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
            valid.replace('"schema_version": 1', '"schema_version": true'),
            valid.replace('"schema_version": 1', '"schema_version": 2'),
            valid.replace('"schema_version": 1', '"schema_version": 1, "extra": 0'),
            valid.replace('"again"', '"first"'),
            valid.replace('/v1/events', '/v1/%2e%2e/events'),
            valid.replace('/v1/events', '//v1/events'),
            valid.replace('750', 'NaN'),
            valid.replace('750', 'Infinity'),
            valid.replace('"expect_status": 200', '"expect_status": true'),
            valid.replace('"equals": 1', '"length": true'),
            json.dumps(dict(json.loads(valid), steps=json.loads(valid)["steps"][:2])),
            '{"schema_version":',
            valid + " " * 65536,
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contract.json"
            for case in cases:
                with self.subTest(case=case[:100]):
                    path.write_text(case)
                    receipt, code = verify(path, "http://127.0.0.1:8765", True)
                    self.assertEqual((receipt["verdict"], code), ("INVALID", 3))
                    self.assertEqual(receipt["executed_steps"], 0)

    def test_incomplete_responses(self):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_POST(self):
                self.send_response(200)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def do_GET(self):
                if reply is None:
                    return
                status, media, body = reply
                self.send_response(status)
                self.send_header("Content-Type", media)
                self.send_header("Location", "http://example.com:8765")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        path = EXAMPLES / "webhook-idempotency.json"
        with HTTPServer(("127.0.0.1", 0), Handler) as server, serving(server) as url:
            for reply in (None, (301, "application/json", b"{}"), (302, "application/json", b"{}"),
                          (200, "text/plain", b'{"credited_cents":750,"ledger_rows":1}'),
                          (200, "application/json", b"{"),
                          (200, "application/json", b"{}"),
                          (200, "application/json", b" " * 262145)):
                with self.subTest(reply_size=len(reply[2]) if reply else None):
                    self.assertEqual(verify(path, url, True)[1], 2)
        with socket.socket() as reserved:
            reserved.bind(("127.0.0.1", 0))
            self.assertEqual(verify(path, f"http://127.0.0.1:{reserved.getsockname()[1]}", True)[1], 2)


    def test_timeout_is_unverified(self):
        release = Event()

        class SilentHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                release.wait(5)

        with HTTPServer(("127.0.0.1", 0), SilentHandler) as server, serving(server) as url:
            try:
                result, code = verify(EXAMPLES / "webhook-idempotency.json", url, True)
                self.assertEqual((result["verdict"], code, result["skipped_assertions"]), ("UNVERIFIED", 2, 2))
            finally:
                release.set()
