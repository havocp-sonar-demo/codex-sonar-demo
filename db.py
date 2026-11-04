import sqlite3

DB_PATH = "invoices.db"


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS invoices ("
        "id INTEGER PRIMARY KEY, owner TEXT, customer TEXT, amount REAL)"
    )
    if conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO invoices (owner, customer, amount) VALUES (?, ?, ?)",
            [
                ("alice", "Acme Corp", 1200.0),
                ("alice", "Globex", 340.5),
                ("bob", "Initech", 99.99),
                ("bob", "Umbrella", 5000.0),
            ],
        )
    conn.commit()


def query_invoices(where):
    """Return invoices matching a raw SQL WHERE clause."""
    conn = connect()
    try:
        init_db(conn)
        rows = conn.execute("SELECT * FROM invoices WHERE " + where).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
