import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from risk_lab.demo_http import demo_server
from risk_lab.http_verify import verify
from risk_lab.sqlite_witness import count_rows, definition
from test_outcomelab import serving
from test_stateful_http import WEBHOOK


class SQLiteWitnessTests(unittest.TestCase):
    def test_deceptive_http_pass_needs_database_witness(self):
        hashes = set()
        for variant, verdict in (("broken", "FAIL"), ("fixed", "PASS")):
            with self.subTest(variant=variant), demo_server(variant, mask_ledger=True) as server, serving(server) as url:
                self.assertEqual(verify(WEBHOOK, url, True)[1], 0)
                args = [str(server.ledger_db.resolve()), "ledger", "invoice_id", "1"]
                for _ in range(2):
                    cli = os.environ.get("OUTCOMELAB_TEST_CLI")
                    if cli:
                        with tempfile.TemporaryDirectory() as cwd:
                            run = subprocess.run([cli, "verify-http", "--contract", WEBHOOK, "--base-url", url,
                                                  "--allow-local-writes", "--sqlite-witness", *args,
                                                  "--allow-disposable-witness", "--json"],
                                                 cwd=cwd, capture_output=True, text=True, timeout=15)
                        receipt, code = json.loads(run.stdout), run.returncode
                    else:
                        receipt, code = verify(WEBHOOK, url, True, witness_arguments=args, allow_witness=True)
                    self.assertEqual((receipt["verdict"], code), (verdict, int(verdict == "FAIL")), receipt)
                    self.assertEqual(receipt["sqlite_witness"]["authority"], "read-only-local-sqlite")
                    self.assertEqual(receipt["sqlite_witness"]["baseline"], "PASS")
                    self.assertEqual(receipt["sqlite_witness"]["readback"], verdict)
                    self.assertTrue(all(item["status"] == "PASS" for item in receipt["assertion_results"]))
                    self.assertNotIn(args[0], json.dumps(receipt))
                    hashes.add(receipt["contract_sha256"])
                    print(f"Deceptive ledger {variant}: HTTP assertions PASS, SQLite {verdict}, "
                          f"contract={receipt['contract_sha256']}", flush=True)
        self.assertEqual(len(hashes), 1)

    def test_invalid_or_unavailable_witness_stops_before_requests(self):
        with tempfile.TemporaryDirectory() as root, patch("risk_lab.http_verify.request") as request:
            path = str((Path(root) / "missing.sqlite").resolve())
            args = [path, "ledger", "invoice_id", "1"]
            url = "http://127.0.0.1:8765"
            self.assertEqual(verify(WEBHOOK, url, True, witness_arguments=args)[1], 3)
            result, code = verify(WEBHOOK, url, True, witness_arguments=args, allow_witness=True)
            self.assertEqual((code, result["sqlite_witness"]["baseline"]), (2, "UNVERIFIED"))
            self.assertFalse(Path(path).exists())
            args[1] = 'ledger"; DELETE FROM ledger'
            self.assertEqual(verify(WEBHOOK, url, True, witness_arguments=args, allow_witness=True)[1], 3)
            request.assert_not_called()

    def test_view_and_wal_are_refused(self):
        with tempfile.TemporaryDirectory() as root:
            path = (Path(root) / "witness.sqlite").resolve()
            with closing(sqlite3.connect(path)) as db:
                db.executescript("CREATE TABLE ledger (run_id TEXT); CREATE VIEW fake AS SELECT * FROM ledger;")
                before = path.read_bytes()
                good = definition([str(path), "ledger", "run_id", "1"])
                self.assertEqual(count_rows(good, "example")[1], 0)
                self.assertEqual(path.read_bytes(), before)
                with self.assertRaises(ValueError):
                    count_rows(definition([str(path), "fake", "run_id", "1"]), "example")
                db.execute("PRAGMA journal_mode=WAL").fetchone()
            with self.assertRaises(ValueError):
                count_rows(good, "example")

    def test_unavailable_final_witness_cannot_pass(self):
        with demo_server("fixed") as server, serving(server) as url:
            args = [str(server.ledger_db.resolve()), "ledger", "invoice_id", "1"]
            with patch("risk_lab.sqlite_witness.count_rows", side_effect=[((1, 2), 0), sqlite3.OperationalError]):
                receipt, code = verify(WEBHOOK, url, True, witness_arguments=args, allow_witness=True)
            self.assertEqual((receipt["verdict"], code, receipt["sqlite_witness"]["readback"]),
                             ("UNVERIFIED", 2, "UNVERIFIED"))
            self.assertEqual(receipt["executed_steps"], 6)


    def test_proven_failure_survives_interrupted_later_write(self):
        headers = (200, "application/json")
        with patch("risk_lab.http_verify.request", side_effect=[
            (*headers, b'{"credited_cents":0,"ledger_rows":0}'),
            (*headers, b'{"event_id":"event"}'),
            (*headers, b'{"credited_cents":1500,"ledger_rows":2}'),
            OSError,
        ]) as request:
            receipt, code = verify(WEBHOOK, "http://127.0.0.1:8765", True)
        self.assertEqual((receipt["verdict"], code), ("FAIL", 1))
        self.assertTrue(receipt["effect_unknown"])
        self.assertEqual(receipt["error_class"], "incomplete_observation")
        self.assertEqual(request.call_count, 4)
        self.assertEqual(receipt["skipped_steps"], 2)
