"""Regression tests for the two executable negative-control demonstrations."""
from __future__ import annotations

import contextlib
from contextlib import closing
from io import StringIO
import json
import sqlite3
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from risk_lab import CONTRACTS, run_all, run_scenario
from risk_lab import fixtures
from risk_lab.__main__ import main
from risk_lab.runner import _run_case


class ProductionRiskLabTests(unittest.TestCase):
    def test_two_scenarios_are_registered(self):
        self.assertEqual(set(CONTRACTS), {"webhook-idempotency", "invoice-persistence"})

    def test_duplicate_webhook_negative_control_fails(self):
        result = run_scenario("webhook-idempotency")
        self.assertEqual(result.negative_control.status, "FAIL")
        self.assertEqual(result.negative_control.measurements["ledger_rows"], 2)
        self.assertEqual(result.negative_control.measurements["credited_cents"], 1500)

    def test_duplicate_webhook_corrected_passes(self):
        result = run_scenario("webhook-idempotency")
        self.assertEqual(result.corrected.status, "PASS")
        self.assertEqual(result.corrected.measurements["ledger_rows"], 1)
        self.assertEqual(result.corrected.measurements["credited_cents"], 750)
        self.assertEqual(result.corrected.measurements["second_delivery"], "duplicate")

    def test_invoice_persistence_negative_control_fails(self):
        result = run_scenario("invoice-persistence")
        self.assertEqual(result.negative_control.status, "FAIL")
        self.assertTrue(result.negative_control.measurements["acknowledged"])
        self.assertFalse(result.negative_control.measurements["row_found_after_reopen"])

    def test_invoice_persistence_corrected_passes(self):
        result = run_scenario("invoice-persistence")
        self.assertEqual(result.corrected.status, "PASS")
        self.assertEqual(result.corrected.measurements["amount_cents_after_reopen"], 1250)

    def test_unknown_scenario_not_accepted(self):
        with self.assertRaises(ValueError):
            run_scenario("invented-case")

    def test_invalid_invoice_does_not_count_as_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            def fail_handler(*_args):
                raise ValueError("invalid input")
            result = _run_case("bad", fail_handler, Path(temp), "invoice-persistence")
        self.assertEqual(result.status, "UNVERIFIED")
        self.assertIsNone(result.invariant_met)

    def test_webhook_rejects_nonpositive_or_boolean_amount(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "db.sqlite"
            fixtures.initialize_webhook_db(db)
            for amount in (0, -1, True, "750"):
                with self.subTest(amount=amount), self.assertRaises(ValueError):
                    fixtures.apply_webhook_fixed(db, "evt-1", "inv-demo", amount)

    def test_duplicate_event_conflicting_invoice_or_amount_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "db.sqlite"
            fixtures.initialize_webhook_db(db)
            self.assertEqual(fixtures.apply_webhook_fixed(db, "evt-123", "inv-demo", 750), "accepted")
            for invoice, amount in (("inv-demo", 999), ("other", 750)):
                with self.subTest(invoice=invoice, amount=amount), self.assertRaises(ValueError):
                    fixtures.apply_webhook_fixed(db, "evt-123", invoice, amount)
            with closing(sqlite3.connect(db)) as cx:
                self.assertEqual(cx.execute("SELECT COUNT(*) FROM ledger").fetchone()[0], 1)
                self.assertEqual(cx.execute("SELECT credited_cents FROM invoices WHERE id='inv-demo'").fetchone()[0], 750)

    def test_webhook_unknown_invoice_rolls_back_event_registration(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / "db.sqlite"
            fixtures.initialize_webhook_db(db)
            with self.assertRaises(ValueError):
                fixtures.apply_webhook_fixed(db, "evt-missing", "does-not-exist", 750)
            with closing(sqlite3.connect(db)) as cx:
                self.assertEqual(cx.execute("SELECT COUNT(*) FROM processed_events").fetchone()[0], 0)

    def test_all_results_include_digest_and_limitations(self):
        results = run_all()
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertEqual(result.verdict, "DEMONSTRATED")
            self.assertEqual(len(result.contract_sha256), 64)
            self.assertEqual(len(result.source_sha256), 64)
            self.assertTrue(result.limitations)

    def test_cli_json_output_and_exit(self):
        stream = StringIO()
        with contextlib.redirect_stdout(stream):
            exit_code = main(["--json"])
        self.assertEqual(exit_code, 0)
        data = json.loads(stream.getvalue())
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(len(data["results"]), 2)

    def test_cli_returns_failure_when_regression(self):
        failed = run_scenario("webhook-idempotency")
        from dataclasses import replace
        failure = replace(failed, verdict="REGRESSION")
        stream = StringIO()
        with patch("risk_lab.__main__.run_all", return_value=[failure]), contextlib.redirect_stdout(stream):
            exit_code = main([])
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
