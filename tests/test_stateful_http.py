import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

from risk_lab.cli import main
from risk_lab.contracts import load_contract
from risk_lab.demo_http import demo_server
from risk_lab.http_verify import verify
from test_outcomelab import EXAMPLES, serving

V2 = EXAMPLES / "v2"
WEBHOOK = V2 / "webhook-idempotency.json"
INVOICE = V2 / "invoice-persistence.json"


class StatefulHTTPTests(unittest.TestCase):
    def test_same_contract_twice_without_reset(self):
        executable = os.environ.get("OUTCOMELAB_TEST_CLI")
        with tempfile.TemporaryDirectory() as directory:
            self.exercise_both_variants(executable, directory)

    def exercise_both_variants(self, executable, directory):
        for contract in (WEBHOOK, INVOICE):
            hashes = set()
            runs = set()
            for variant, verdict, code in (("broken", "FAIL", 1), ("fixed", "PASS", 0)):
                with self.subTest(contract=contract.stem, variant=variant):
                    with demo_server(variant) as server, serving(server) as url:
                        for _ in range(2):
                            if executable:
                                child = subprocess.run([executable, "verify-http", "--contract", contract,
                                                        "--base-url", url, "--allow-local-writes", "--json"],
                                                       cwd=directory, capture_output=True, text=True, timeout=25)
                                result, exit_code = json.loads(child.stdout), child.returncode
                            else:
                                result, exit_code = verify(contract, url, True)
                            self.assertEqual((result["verdict"], exit_code), (verdict, code), result)
                            self.assertEqual(result["observation_authority"], "target-http-api")
                            self.assertEqual(result["step_results"][0]["phase"], "baseline")
                            self.assertEqual(result["skipped_steps"], 0)
                            if contract == WEBHOOK:
                                self.assertEqual(result["step_results"][-2]["observed_status"], 400)
                                self.assertEqual(result["executed_assertions"], 7)
                            if verdict == "PASS":
                                self.assertEqual(result["skipped_assertions"], 0)
                            if executable:
                                print(f"{contract.stem} {variant}: {result['verdict']} "
                                      f"sha256={result['contract_sha256']} "
                                      f"steps={result['executed_steps']} "
                                      f"assertions={result['executed_assertions']} "
                                      f"skipped={result['skipped_assertions']}", flush=True)
                            hashes.add(result["contract_sha256"])
                            runs.add(result["run_id"])
            self.assertEqual(len(hashes), 1)
            self.assertEqual(len(runs), 4)

    def test_stale_resource_stops_before_mutation(self):
        for contract in (WEBHOOK, INVOICE):
            with self.subTest(contract=contract.stem), demo_server("fixed") as server, serving(server) as url:
                with patch("risk_lab.http_verify.uuid4", return_value=UUID(int=1)):
                    self.assertEqual(verify(contract, url, True)[1], 0)
                    result, code = verify(contract, url, True)
                self.assertEqual((result["verdict"], code), ("UNVERIFIED", 2))
                self.assertEqual(result["attempted_steps"], 1)

    def test_rejects_invalid_v2_contracts(self):
        source = WEBHOOK.read_text(encoding="utf-8")
        substitutions = (
            ('"schema_version": 2', '"schema_version": 2, "schema_version": 2'),
            ('"schema_version": 2', '"schema_version": true'),
            ('"schema_version": 2', '"schema_version": 2, "headers": {}'),
            ('"delta": 750', '"delta": true'),
            ('"delta": 750', '"delta": NaN'),
            ('"delta": 750', '"delta": Infinity'),
            ('"amount_cents": 750', '"amount_cents": "' + "a" * 16500 + '"'),
            ('"/event_id"', '"/../event_id"'),
            ('"{accepted_event}"', '"{missing}"'),
            ('"/v1/events"', '"/v1/%2e%2e/events"'),
            ('"name": "accepted_event"', '"name": "run_id"'),
            ('"from": "once"', '"from": "after"'),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.json"
            for old, new in substitutions:
                with self.subTest(new=new[:100]):
                    path.write_text(source.replace(old, new, 1), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        load_contract(path)
        with self.assertRaises(ValueError):
            load_contract(V2 / "invalid" / "unknown-resource.json")

    def test_incomplete_observation_after_action(self):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def respond(self, data):
                body = json.dumps(data).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                if mode == "framing":
                    self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                self.respond({"credited_cents": 0, "ledger_rows": 0} if mode != "baseline" else {})

            def do_POST(self):
                if mode == "reset":
                    return
                self.rfile.read(int(self.headers["Content-Length"]))
                self.respond({"event_id": "../wrong"} if mode == "capture" else {})

        for mode, attempts, completed in (("baseline", 1, 1), ("missing", 2, 2), ("capture", 2, 2),
                                          ("reset", 2, 1), ("framing", 1, 0)):
            with self.subTest(mode=mode), HTTPServer(("127.0.0.1", 0), Handler) as server, serving(server) as url:
                result, code = verify(WEBHOOK, url, True)
                self.assertEqual((result["verdict"], code), ("UNVERIFIED", 2))
                self.assertEqual((result["attempted_steps"], result["executed_steps"]), (attempts, completed))
                self.assertEqual(result["skipped_steps"], 6 - attempts)
                self.assertGreater(result["skipped_assertions"], 0)
                self.assertNotIn("../wrong", json.dumps(result))


    def test_validate_has_no_network_or_subprocess(self):
        for path, expected in ((INVOICE, 0), (V2 / "invalid" / "unknown-resource.json", 3)):
            output = io.StringIO()
            with (patch("socket.socket", side_effect=AssertionError("unexpected socket")),
                  patch("subprocess.run", side_effect=AssertionError("unexpected command")),
                  contextlib.redirect_stdout(output)):
                self.assertEqual(main(["validate", "--contract", str(path), "--json"]), expected)
            self.assertEqual(json.loads(output.getvalue())["verdict"], "VALID" if expected == 0 else "INVALID")

    def test_opt_in_bearer_and_captured_path(self):
        token = "test-secret.Ab_123"
        requests = []
        records = {}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def reply(self, status, body):
                raw = json.dumps(body).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def authorized(self):
                requests.append(self.headers.get("Authorization"))
                if requests[-1] == f"Bearer {token}":
                    return True
                self.reply(401, {"error": token})
                return False

            def do_POST(self):
                if self.authorized():
                    body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                    records[body["invoice_id"]] = body
                    self.reply(200, {"invoice_id": body["invoice_id"], "secret": token})

            def do_GET(self):
                if self.authorized():
                    row = records.get(self.path.rsplit("/", 1)[-1])
                    self.reply(200 if row else 404, row or {})

        contract = json.loads(INVOICE.read_text(encoding="utf-8"))
        contract["steps"][1]["capture"] = {"name": "created", "pointer": "/invoice_id"}
        observe = contract["steps"][-1]
        contract["steps"].insert(2, dict(observe, id="captured", path="/v1/invoices/{created}"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "auth.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            with HTTPServer(("127.0.0.1", 0), Handler) as server, serving(server) as url:
                for invalid in ("", token + "\r\nInjected: value", "a" * 2051):
                    with patch.dict(os.environ, {"OUTCOMELAB_BEARER_TOKEN": invalid}):
                        self.assertEqual(verify(path, url, True, True)[1], 3)
                self.assertEqual(requests, [])
                with patch.dict(os.environ, {"OUTCOMELAB_BEARER_TOKEN": token}):
                    self.assertEqual(verify(path, url, True)[1], 2)
                    self.assertEqual(requests, [None])
                    stdout, stderr = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        code = main(["verify-http", "--contract", str(path), "--base-url", url,
                                     "--allow-local-writes", "--bearer-token", "--json"])
                self.assertEqual(code, 0)
                self.assertEqual(requests[1:], [f"Bearer {token}"] * 4)
                self.assertNotIn(token, stdout.getvalue() + stderr.getvalue())
