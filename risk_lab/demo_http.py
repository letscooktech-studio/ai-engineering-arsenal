"""Disposable OutcomeLab HTTP reference service, backed by temporary SQLite."""
import argparse
import json
import re
import sqlite3
from contextlib import closing, contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

from . import fixtures
from .contracts import ID, decode, matches, require


@contextmanager
def demo_server(variant, port=0):
    with TemporaryDirectory(prefix="outcomelab-") as directory:
        webhook = Path(directory) / "webhook.sqlite"
        invoice = Path(directory) / "invoice.sqlite"
        fixtures.initialize_webhook_db(webhook)
        fixtures.initialize_invoice_db(invoice)
        apply = fixtures.apply_webhook_broken if variant == "broken" else fixtures.apply_webhook_fixed
        save = fixtures.save_invoice_broken if variant == "broken" else fixtures.save_invoice_fixed
        events = {}
        with closing(sqlite3.connect(invoice)) as db, db:
            db.execute("CREATE TABLE inventory (sku TEXT PRIMARY KEY, available INTEGER NOT NULL)")

        class Handler(BaseHTTPRequestHandler):
            def setup(self):
                self.request.settimeout(2)
                super().setup()

            def log_message(self, *_):
                pass

            def send_json(self, status, data):
                raw = json.dumps(data).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def reserve_stock(self, body):
                require(type(body) is dict and set(body) == {"sku", "quantity"})
                sku, quantity = body["sku"], body["quantity"]
                require(matches(ID, sku) and type(quantity) is int and 0 < quantity <= 5)
                with closing(sqlite3.connect(invoice)) as db, db:
                    db.execute("INSERT OR IGNORE INTO inventory VALUES (?, 5)", (sku,))
                    available = db.execute("SELECT available FROM inventory WHERE sku=?", (sku,)).fetchone()[0]
                    accepted = quantity <= available
                    if accepted or variant == "broken":
                        db.execute("UPDATE inventory SET available = available - ? WHERE sku=?", (quantity, sku))
                self.send_json(200 if accepted else 409, {"accepted": accepted})

            def do_POST(self):
                if self.path not in ("/v1/events", "/v1/invoices", "/v1/reservations"):
                    self.send_json(404, {})
                    return
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                    require(0 < size <= 16384 and self.headers.get_content_type() == "application/json")
                    body = decode(self.rfile.read(size))
                    if self.path == "/v1/reservations":
                        self.reserve_stock(body)
                        return
                    is_event = self.path == "/v1/events"
                    key = "event_id" if is_event else "customer"
                    require(type(body) is dict and set(body) == {key, "invoice_id", "amount_cents"})
                    name, invoice_id, cents = body[key], body["invoice_id"], body["amount_cents"]
                    require(matches(ID, name) and matches(ID, invoice_id))
                    require(type(cents) is int and 0 < cents <= 1_000_000_000)
                    if is_event:
                        isolated = re.fullmatch(r"[0-9a-f]{32}", invoice_id)
                        require(invoice_id == "inv-demo" or isolated)
                        if isolated:
                            with closing(sqlite3.connect(webhook)) as db, db:
                                db.execute("INSERT OR IGNORE INTO invoices(id) VALUES (?)", (invoice_id,))
                        require(events.get(name, (invoice_id, cents)) == (invoice_id, cents))
                        apply(webhook, name, invoice_id, cents)
                        events[name] = (invoice_id, cents)
                    else:
                        save(invoice, invoice_id, name, cents)
                except (ValueError, sqlite3.IntegrityError, RecursionError):
                    self.send_json(400, {})
                    return
                self.send_json(200, {"accepted": True, **({"event_id": name} if is_event else {})})

            def do_GET(self):
                route = re.fullmatch(rf"/v1/(ledger|invoices|inventory)/({ID})", self.path)
                if not route:
                    self.send_json(404, {})
                    return
                kind, invoice_id = route.groups()
                with closing(sqlite3.connect(webhook if kind == "ledger" else invoice)) as db:
                    if kind == "ledger":
                        row = db.execute(
                            "SELECT credited_cents, (SELECT COUNT(*) FROM ledger WHERE invoice_id=?) "
                            "FROM invoices WHERE id=?", (invoice_id, invoice_id)).fetchone()
                        keys = ("credited_cents", "ledger_rows")
                        if row is None and re.fullmatch(r"[0-9a-f]{32}", invoice_id):
                            row = (0, 0)
                    elif kind == "inventory":
                        row = db.execute("SELECT available FROM inventory WHERE sku=?", (invoice_id,)).fetchone()
                        row = row or (5,)
                        keys = ("available",)
                    else:
                        row = db.execute("SELECT id, amount_cents FROM invoices WHERE id=?",
                                         (invoice_id,)).fetchone()
                        keys = ("invoice_id", "amount_cents")
                self.send_json(200 if row else 404, dict(zip(keys, row)) if row else {})

        with HTTPServer(("127.0.0.1", port), Handler) as server:
            yield server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", required=True, choices=["broken", "fixed"])
    parser.add_argument("--port", required=True, type=int, choices=range(1024, 65536), metavar="PORT")
    args = parser.parse_args()
    with demo_server(args.variant, args.port) as server:
        print(f"OutcomeLab disposable {args.variant} service at http://127.0.0.1:{args.port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
