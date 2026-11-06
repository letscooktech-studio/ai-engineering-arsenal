"""Deterministic, dependency-free regression demonstrations.

Only repository-owned, explicitly registered synthetic fixtures can execute.
This engine does not execute third-party repositories, arbitrary commands, or LLM output.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile
from typing import Callable

from . import fixtures


@dataclass(frozen=True)
class Observation:
    label: str
    status: str
    invariant_met: bool | None
    measurements: dict[str, int | bool | str]
    error: str | None = None


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    verdict: str
    negative_control: Observation
    corrected: Observation
    contract_sha256: str
    source_sha256: str
    limitations: tuple[str, ...]

    def as_json(self) -> dict:
        return asdict(self)


CONTRACTS = {
    "webhook-idempotency": {
        "schema_version": 1,
        "id": "webhook-idempotency",
        "invariant": "One event delivered twice creates exactly one ledger row and one credit",
        "scope": "Synthetic SQLite event handler, sequential duplicate deliveries, reopened database connection",
    },
    "invoice-persistence": {
        "schema_version": 1,
        "id": "invoice-persistence",
        "invariant": "An acknowledged save remains visible when a fresh database connection is opened",
        "scope": "Synthetic SQLite persistence, no UI or full application restart",
    },
}


def _run_webhook(label: str, handler: Callable, root: Path) -> Observation:
    path = root / f"{label}.sqlite"
    fixtures.initialize_webhook_db(path)
    results = [handler(path, "evt-123", "inv-demo", 750), handler(path, "evt-123", "inv-demo", 750)]
    with closing(sqlite3.connect(path)) as connection:
        paid = connection.execute("SELECT credited_cents FROM invoices WHERE id='inv-demo'").fetchone()[0]
        ledger = connection.execute("SELECT COUNT(*) FROM ledger").fetchone()[0]
        unique = connection.execute("SELECT COUNT(*) FROM processed_events").fetchone()[0]
    measurements = {"credited_cents": paid, "ledger_rows": ledger, "processed_event_rows": unique, "second_delivery": results[1]}
    valid = paid == 750 and ledger == 1 and results[1] == "duplicate"
    return Observation(label, "PASS" if valid else "FAIL", valid, measurements)


def _run_persistence(label: str, handler: Callable, root: Path) -> Observation:
    path = root / f"{label}.sqlite"
    fixtures.initialize_invoice_db(path)
    acknowledged = handler(path, "inv-123", "Test Customer", 1250)
    with closing(sqlite3.connect(path)) as reopened_connection:
        row = reopened_connection.execute("SELECT id, customer, amount_cents FROM invoices WHERE id=?", ("inv-123",)).fetchone()
    valid = acknowledged is True and row == ("inv-123", "Test Customer", 1250)
    measurements: dict[str, int | bool | str] = {"acknowledged": acknowledged, "row_found_after_reopen": row is not None}
    if row is not None:
        measurements["amount_cents_after_reopen"] = row[2]
    return Observation(label, "PASS" if valid else "FAIL", valid, measurements)


def _run_case(label: str, implementation: Callable, root: Path, scenario_id: str) -> Observation:
    try:
        if scenario_id == "webhook-idempotency":
            return _run_webhook(label, implementation, root)
        if scenario_id == "invoice-persistence":
            return _run_persistence(label, implementation, root)
        return Observation(label, "UNVERIFIED", None, {}, "Unknown scenario")
    except (ValueError, sqlite3.Error, OSError) as exc:
        # Exceptions are not automatically a proof of a desired negative control.
        return Observation(label, "UNVERIFIED", None, {}, f"{type(exc).__name__}: {exc}")


IMPLEMENTATIONS = {
    "webhook-idempotency": (fixtures.apply_webhook_broken, fixtures.apply_webhook_fixed),
    "invoice-persistence": (fixtures.save_invoice_broken, fixtures.save_invoice_fixed),
}
LIMITATIONS = (
    "Synthetic reference fixtures only: no external application, browser, API, or financial provider tested.",
    "Fixture and test code are owned by the same repository, not independently approved.",
    "A passing corrected demonstration is not proof of production security or reliability.",
)


def run_scenario(scenario_id: str) -> ScenarioResult:
    if scenario_id not in CONTRACTS:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    contract = CONTRACTS[scenario_id]
    contract_digest = sha256(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    source_digest = sha256(Path(fixtures.__file__).read_bytes()).hexdigest()
    broken, fixed = IMPLEMENTATIONS[scenario_id]
    with tempfile.TemporaryDirectory(prefix="arsenal-risk-lab-") as directory:
        root = Path(directory)
        negative = _run_case("broken", broken, root, scenario_id)
        corrected = _run_case("fixed", fixed, root, scenario_id)
    verdict = (
        "DEMONSTRATED" if negative.status == "FAIL" and corrected.status == "PASS"
        else "UNVERIFIED" if "UNVERIFIED" in (negative.status, corrected.status)
        else "REGRESSION"
    )
    return ScenarioResult(scenario_id, verdict, negative, corrected, contract_digest, source_digest, LIMITATIONS)


def run_all() -> list[ScenarioResult]:
    return [run_scenario(name) for name in sorted(CONTRACTS)]
