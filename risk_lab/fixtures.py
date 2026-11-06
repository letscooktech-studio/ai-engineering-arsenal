"""Synthetic intentionally flawed and corrected implementations for controlled demos.

These implementations are not reusable production payment or invoicing components.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path


def initialize_webhook_db(path: Path) -> None:
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.executescript("""
        CREATE TABLE invoices (id TEXT PRIMARY KEY, credited_cents INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT NOT NULL,
            provider_event_id TEXT NOT NULL,
            amount_cents INTEGER NOT NULL
        );
        CREATE TABLE processed_events (
            provider_event_id TEXT PRIMARY KEY,
            invoice_id TEXT NOT NULL,
            amount_cents INTEGER NOT NULL
        );
        INSERT INTO invoices (id, credited_cents) VALUES ('inv-demo', 0);
        """)


def apply_webhook_broken(path: Path, event_id: str, invoice_id: str, cents: int) -> str:
    """Intentionally broken: records each delivery as a new financial effect."""
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute(
            "INSERT INTO ledger(invoice_id, provider_event_id, amount_cents) VALUES (?, ?, ?)",
            (invoice_id, event_id, cents),
        )
        connection.execute(
            "UPDATE invoices SET credited_cents = credited_cents + ? WHERE id = ?",
            (cents, invoice_id),
        )
    return "accepted"


def apply_webhook_fixed(path: Path, event_id: str, invoice_id: str, cents: int) -> str:
    """Simplified synthetic correction: event deduplication within one SQLite transaction."""
    if not event_id or not invoice_id or isinstance(cents, bool) or not isinstance(cents, int) or cents <= 0:
        raise ValueError("Expected positive integer amount and nonempty event and invoice IDs")
    with closing(sqlite3.connect(path, timeout=5)) as connection, connection:
        # The primary key is the actual idempotency barrier, not an in-memory flag.
        inserted = connection.execute(
            "INSERT OR IGNORE INTO processed_events(provider_event_id, invoice_id, amount_cents) VALUES (?, ?, ?)",
            (event_id, invoice_id, cents),
        )
        if inserted.rowcount == 0:
            previous = connection.execute(
                "SELECT invoice_id, amount_cents FROM processed_events WHERE provider_event_id=?", (event_id,)
            ).fetchone()
            if previous != (invoice_id, cents):
                raise ValueError("Conflicting payload for existing event ID")
            return "duplicate"
        cursor = connection.execute(
            "UPDATE invoices SET credited_cents = credited_cents + ? WHERE id = ?",
            (cents, invoice_id),
        )
        if cursor.rowcount != 1:
            raise ValueError("Unknown invoice")
        connection.execute(
            "INSERT INTO ledger(invoice_id, provider_event_id, amount_cents) VALUES (?, ?, ?)",
            (invoice_id, event_id, cents),
        )
    return "accepted"


def initialize_invoice_db(path: Path) -> None:
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("CREATE TABLE invoices (id TEXT PRIMARY KEY, customer TEXT NOT NULL, amount_cents INTEGER NOT NULL)")


def save_invoice_broken(path: Path, invoice_id: str, customer: str, cents: int) -> bool:
    """Intentionally broken: acknowledges the operation without persisting it."""
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("INSERT INTO invoices(id, customer, amount_cents) VALUES (?, ?, ?)", (invoice_id, customer, cents))
        connection.rollback()
    return True


def save_invoice_fixed(path: Path, invoice_id: str, customer: str, cents: int) -> bool:
    """Simple durable SQLite write for the synthetic demonstration."""
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("INSERT INTO invoices(id, customer, amount_cents) VALUES (?, ?, ?)", (invoice_id, customer, cents))
    return True
