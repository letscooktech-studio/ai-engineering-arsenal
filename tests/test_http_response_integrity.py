import gzip
import json
import os
import socketserver
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from threading import Thread

CONTRACT = Path(__file__).resolve().parents[1] / "examples/http/v2/webhook-idempotency.json"
HEADER_ERROR = "malformed_response_headers"
ENCODING_ERROR = "unsupported_content_encoding"


class ResponseIntegrityTests(unittest.TestCase):
    def run_wire_case(self, *, suffix=b"", fault_at=1, encode=False, length_extra=0,
                      status=b"HTTP/1.1 200 OK", media=b"application/json"):
        with tempfile.TemporaryDirectory() as directory:
            db = (Path(directory) / "ledger.sqlite").resolve()
            with closing(sqlite3.connect(db)) as connection:
                connection.execute("CREATE TABLE ledger (invoice_id TEXT, amount_cents INTEGER)")
            calls = []

            class Responder(socketserver.StreamRequestHandler):
                def handle(self):
                    self.request.settimeout(2)
                    method, path, _ = self.rfile.readline().split()
                    length = 0
                    while (line := self.rfile.readline()) not in (b"", b"\r\n"):
                        if line.lower().startswith(b"content-length:"):
                            length = int(line.split(b":", 1)[1])
                    body = self.rfile.read(length)
                    calls.append(method)
                    reply_status = b"HTTP/1.1 200 OK"
                    with closing(sqlite3.connect(db)) as connection, connection:
                        if method == b"POST":
                            payload = json.loads(body)
                            identity = payload["invoice_id"]
                            if payload["amount_cents"] != 750:
                                reply_status = b"HTTP/1.1 400 Bad Request"
                            else:
                                connection.execute(
                                    "INSERT INTO ledger SELECT ?, 750 WHERE NOT EXISTS "
                                    "(SELECT 1 FROM ledger WHERE invoice_id=?)", (identity, identity)
                                )
                            response = {"event_id": payload["event_id"]}
                        else:
                            count, amount = connection.execute(
                                "SELECT count(*), coalesce(sum(amount_cents), 0) FROM ledger WHERE invoice_id=?",
                                (path.rsplit(b"/", 1)[-1].decode(),),
                            ).fetchone()
                            response = {"ledger_rows": count, "credited_cents": amount}
                    data = json.dumps(response).encode()
                    fault = len(calls) == fault_at
                    if fault and encode:
                        data = gzip.compress(data, mtime=0)
                    if fault and reply_status.endswith(b"200 OK"):
                        reply_status = status
                    content_type = media if fault else b"application/json"
                    size = str(len(data) + (length_extra if fault else 0)).encode()
                    wire = (reply_status + b"\r\nContent-Type: " + content_type +
                            b"\r\nContent-Length: " + size + b"\r\n" +
                            (suffix if fault else b"") + b"\r\n" + data)
                    self.wfile.write(wire)

            with socketserver.TCPServer(("127.0.0.1", 0), Responder) as server:
                worker = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
                worker.start()
                try:
                    executable = os.environ.get("OUTCOMELAB_TEST_CLI")
                    command = [executable] if executable else [sys.executable, "-m", "risk_lab.cli"]
                    run = subprocess.run(
                        [*command, "verify-http", "--contract", CONTRACT, "--base-url",
                         f"http://127.0.0.1:{server.server_address[1]}", "--allow-local-writes",
                         "--sqlite-witness", db, "ledger", "invoice_id", "1",
                         "--allow-disposable-witness", "--sqlite-sum", "amount_cents", "750", "--json"],
                        cwd=directory if executable else CONTRACT.parents[3],
                        capture_output=True, text=True, timeout=15,
                    )
                finally:
                    server.shutdown()
                    worker.join()
            receipt = json.loads(run.stdout)
            self.assertNotIn("secret-sentinel", run.stdout + run.stderr)
            with closing(sqlite3.connect(db)) as connection:
                persisted = connection.execute("SELECT count(*), coalesce(sum(amount_cents),0) FROM ledger").fetchone()
            return run.returncode, receipt, calls, persisted

    def test_well_formed_controls_pass(self):
        for headers, media in ((b"", b"application/json"),
                               (b"Content-Encoding: IdEnTiTy\r\n", b"application/json; charset=utf-8")):
            with self.subTest(headers=headers, media=media):
                code, receipt, calls, persisted = self.run_wire_case(suffix=headers, media=media, fault_at=6)
                self.assertEqual((code, receipt["verdict"], len(calls), persisted), (0, "PASS", 6, (1, 750)))
                self.assertEqual(receipt["sqlite_witness"]["integer_sum"], "PASS")

    def test_malformed_headers_and_unsupported_content_codings_fail_closed(self):
        cases = (
            (b"Broken header\r\n", HEADER_ERROR, False),
            (b"Bad name: secret-sentinel\r\n", HEADER_ERROR, False),
            (b"X-Value: a\x00b\r\n", HEADER_ERROR, False),
            (b"X-Value: a\r\n b\r\n", HEADER_ERROR, False),
            (b"X-Value : a\r\n", HEADER_ERROR, False),
            (b"Content-Encoding: gzip\r\n", ENCODING_ERROR, False),
            (b"Content-Encoding: gzip\r\n", ENCODING_ERROR, True),
            (b"Content-Encoding: br\r\n", ENCODING_ERROR, False),
            (b"Content-Encoding: identity, gzip\r\n", ENCODING_ERROR, False),
            (b"Content-Encoding: identity\r\nContent-Encoding: identity\r\n", ENCODING_ERROR, False),
        )
        for headers, error, encode in cases:
            with self.subTest(headers=headers, encode=encode):
                code, receipt, calls, persisted = self.run_wire_case(suffix=headers, encode=encode, fault_at=6)
                self.assertEqual((code, receipt["verdict"], receipt["error_class"]), (2, "UNVERIFIED", error))
                self.assertEqual((receipt["executed_steps"], len(calls), persisted), (5, 6, (1, 750)))
                self.assertEqual(receipt["sqlite_witness"]["readback"], "SKIPPED")

    def test_invalid_post_response_marks_committed_effect_uncertain_without_retry(self):
        for headers, error in ((b"Broken header\r\n", HEADER_ERROR),
                               (b"Content-Encoding: gzip\r\n", ENCODING_ERROR)):
            with self.subTest(headers=headers):
                code, receipt, calls, persisted = self.run_wire_case(suffix=headers, fault_at=2)
                self.assertEqual((code, receipt["verdict"], receipt["error_class"]), (2, "UNVERIFIED", error))
                self.assertTrue(receipt["effect_unknown"])
                self.assertEqual((receipt["executed_steps"], calls, persisted), (1, [b"GET", b"POST"], (1, 750)))
                self.assertEqual(receipt["executed_assertions"], 2)

    def test_existing_framing_and_content_type_boundaries(self):
        for settings in (
            {"suffix": b"Content-Length: 999\r\n"},
            {"suffix": b"Transfer-Encoding: chunked\r\n"},
            {"suffix": b"Transfer-Encoding: bogus\r\n"},
            {"suffix": b"X-Long: " + b"a" * 65537 + b"\r\n"},
            {"suffix": b"X-Many: a\r\n" * 110},
            {"length_extra": 5},
            {"media": b"text/html"},
            {"status": b"NOTHTTP"},
        ):
            with self.subTest(case=next(iter(settings)), size=len(settings.get("suffix", b""))):
                code, receipt, calls, persisted = self.run_wire_case(**settings)
                self.assertEqual((code, receipt["verdict"], len(calls), persisted), (2, "UNVERIFIED", 1, (0, 0)))
