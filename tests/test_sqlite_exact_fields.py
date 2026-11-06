import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from risk_lab.sqlite_witness import field_definitions
from test_outcomelab import serving
from test_stateful_http import WEBHOOK


class ExactFieldTests(unittest.TestCase):
    def test_wrong_owner_fails_with_correct_http_count_and_sum(self):
        for owner, status, failures in (
            ("Tenant-A", "posted", ["FAIL", "PASS", "PASS"]),
            ("tenant-a", "draft", ["PASS", "FAIL", "PASS"]),
            ("tenant-a", "posted", ["PASS", "PASS", "PASS"]),
        ):
            with self.subTest(owner=owner, status=status), tempfile.TemporaryDirectory() as folder:
                db = (Path(folder) / "ledger.sqlite").resolve()
                with closing(sqlite3.connect(db)) as connection:
                    connection.execute(
                        "CREATE TABLE ledger (invoice_id TEXT PRIMARY KEY, amount_cents INTEGER, "
                        "owner TEXT COLLATE NOCASE, status TEXT, reversed_at TEXT)"
                    )

                class Backend(BaseHTTPRequestHandler):
                    def log_message(self, *_):
                        pass

                    def reply(self, status, body):
                        data = json.dumps(body).encode()
                        self.send_response(status)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(data)))
                        self.end_headers()
                        self.wfile.write(data)

                    def do_POST(self):
                        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                        if payload["amount_cents"] != 750:
                            self.reply(400, {})
                            return
                        with closing(sqlite3.connect(db)) as connection, connection:
                            connection.execute(
                                "INSERT OR IGNORE INTO ledger VALUES (?, 750, ?, ?, NULL)",
                                (payload["invoice_id"], owner, status),
                            )
                        self.reply(200, {"event_id": payload["event_id"]})

                    def do_GET(self):
                        with closing(sqlite3.connect(db)) as connection:
                            present = connection.execute(
                                "SELECT 1 FROM ledger WHERE invoice_id=?", (self.path.rsplit("/", 1)[-1],)
                            ).fetchone() is not None
                        self.reply(200, {"credited_cents": 750 if present else 0, "ledger_rows": int(present)})

                with HTTPServer(("127.0.0.1", 0), Backend) as server, serving(server) as url:
                    executable = os.environ.get("OUTCOMELAB_TEST_CLI")
                    command = [executable] if executable else [sys.executable, "-m", "risk_lab.cli"]
                    child = subprocess.run(
                        [*command, "verify-http", "--contract", WEBHOOK, "--base-url", url,
                         "--allow-local-writes", "--sqlite-witness", db, "ledger", "invoice_id", "1",
                         "--allow-disposable-witness", "--sqlite-sum", "amount_cents", "750",
                         "--sqlite-field", "owner", '"tenant-a"', "--sqlite-field", "status", '"posted"',
                         "--sqlite-field", "reversed_at", "null", "--json"],
                        cwd=folder if executable else WEBHOOK.parents[3],
                        capture_output=True, text=True, timeout=15,
                    )
                result = json.loads(child.stdout)
                self.assertEqual(child.returncode, int("FAIL" in failures), result)
                self.assertTrue(all(check["status"] == "PASS" for check in result["assertion_results"]))
                self.assertEqual(result["sqlite_witness"]["readback"], "PASS")
                self.assertEqual(result["sqlite_witness"]["integer_sum"], "PASS")
                self.assertEqual(result["sqlite_witness"]["exact_fields"],
                                 failures)
                self.assertNotIn("tenant-a", child.stdout + child.stderr)
                self.assertNotIn("Tenant-A", child.stdout + child.stderr)
                with closing(sqlite3.connect(db)) as connection:
                    self.assertEqual(connection.execute(
                        "SELECT amount_cents, owner, status FROM ledger WHERE invoice_id=?", (result["run_id"],)
                    ).fetchone(), (750, owner, status))
                print(f"Stored-field control: HTTP/count/sum PASS, fields {failures}")

    def test_invalid_field_definitions(self):
        for fields in ([("owner", "true")], [("owner", "1.5")], [("owner", "{}")],
                       [("owner", "9223372036854775808")], [("owner", '"a"'), ("OWNER", '"b"')],
                       [('owner"; DROP', '"a"')]):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                field_definitions(fields)
