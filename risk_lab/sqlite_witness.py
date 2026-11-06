"""Operator-scoped counts on disposable, rollback-journal SQLite files."""
import json
import sqlite3
import stat
from contextlib import closing
from hashlib import sha256
from pathlib import Path
from time import monotonic

from .contracts import matches, require


def definition(arguments):
    filename, table, key, expected = arguments
    path = Path(filename)
    require(path.is_absolute() and not str(path).startswith(("//", "\\\\")))
    for name in (table, key):
        require_identifier(name)
    require(matches(r"0|[1-9][0-9]{0,3}", expected))
    return path, table, key, int(expected)


def require_identifier(name):
    require(matches(r"[A-Za-z_][A-Za-z0-9_]{0,63}", name) and not name.lower().startswith("sqlite_"))


def sum_definition(arguments):
    column, expected = arguments
    require_identifier(column)
    require(matches(r"-?(?:0|[1-9][0-9]{0,18})", expected))
    return column, int(expected)


def fingerprint(spec, amount=None):
    path, table, key, expected = spec
    fields = [str(path), table, key, expected]
    if amount is not None:
        fields.append(amount)
    return sha256(json.dumps(fields).encode()).hexdigest()


def count_rows(spec, run_id, identity=None, amount=None):
    path, table, key, expected = spec
    require(path.resolve(strict=True) == path and not str(path).startswith(("//", "\\\\")))
    info = path.stat()
    require(stat.S_ISREG(info.st_mode) and 100 <= info.st_size <= 64 * 1024 * 1024)
    current = info.st_dev, info.st_ino
    require(identity is None or current == identity)
    with path.open("rb") as stream:
        header = stream.read(100)
    require(header[:16] == b"SQLite format 3\x00" and header[18:20] == b"\x01\x01")
    require(not any(path.with_name(path.name + suffix).exists() for suffix in ("-wal", "-shm", "-journal")))
    deadline = monotonic() + 1
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=0.25)) as db:
        db.set_progress_handler(lambda: int(monotonic() >= deadline), 1000)
        db.execute("PRAGMA trusted_schema = OFF")
        # Use a single read snapshot so schema and row checks refer to the same table.
        db.execute("BEGIN")
        require(db.execute(
            "SELECT 1 FROM pragma_table_list WHERE schema='main' AND name=? AND type='table'",
            (table,),
        ).fetchone() is not None)
        require(db.execute(
            "SELECT 1 FROM pragma_table_xinfo(?, 'main') WHERE name=? AND hidden=0", (table, key)
        ).fetchone() is not None)
        predicate = f"""FROM main."{table}" WHERE "{key}" COLLATE BINARY = ? AND typeof("{key}") = 'text' LIMIT ?"""
        parameters = (run_id, max(expected, 1) + 1)
        if amount is None:
            count = db.execute(f"SELECT count(*) FROM (SELECT 1 {predicate})", parameters).fetchone()[0]
        else:
            column, _ = amount
            require(db.execute(
                "SELECT 1 FROM pragma_table_xinfo(?, 'main') WHERE name=? AND hidden=0", (table, column)
            ).fetchone() is not None)
            # Bound rows and sum Python integers exactly without SQLite SUM overflow.
            rows = db.execute(
                f"""SELECT CASE WHEN typeof("{column}") = 'integer' THEN "{column}" END {predicate}""",
                parameters,
            ).fetchall()
            count = len(rows)
            total = None
            if count == expected and all(type(row[0]) is int for row in rows):
                total = sum(row[0] for row in rows)
            count = count, total
    info = path.stat()
    require((info.st_dev, info.st_ino) == current)
    return current, count
