import os
import sqlite3 as sql

SCHEMA = """
CREATE TABLE IF NOT EXISTS persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK (type IN ('INGRESO', 'GASTO', 'DEUDA')),
    amount INTEGER NOT NULL CHECK (amount > 0),
    description TEXT,
    date TEXT NOT NULL DEFAULT (date('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS debts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    involved_person_id INTEGER NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('PROPIA', 'AJENA')),
    max_repayment_date TEXT,
    settled INTEGER NOT NULL DEFAULT 0 CHECK (settled IN (0, 1)),
    settled_at TEXT,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE RESTRICT,
    FOREIGN KEY (involved_person_id) REFERENCES persons(id)
);

CREATE TABLE IF NOT EXISTS debt_increases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    debt_id INTEGER NOT NULL,
    amount INTEGER NOT NULL CHECK (amount > 0),
    description TEXT,
    increased_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (debt_id) REFERENCES debts(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    debt_id INTEGER NOT NULL,
    amount INTEGER NOT NULL CHECK (amount > 0),
    method TEXT NOT NULL CHECK (method IN ('EFECTIVO', 'TRANSFERENCIA', 'TARJETA')),
    date TEXT NOT NULL DEFAULT (date('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (debt_id) REFERENCES debts(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_debts_person ON debts(involved_person_id);
CREATE INDEX IF NOT EXISTS idx_payments_debt ON payments(debt_id);
CREATE INDEX IF NOT EXISTS idx_debt_increases_debt ON debt_increases(debt_id);

CREATE TRIGGER IF NOT EXISTS trg_transactions_no_delete
BEFORE DELETE ON transactions
BEGIN SELECT RAISE(ABORT, 'No se permite eliminar transacciones'); END;

CREATE TRIGGER IF NOT EXISTS trg_debts_no_delete
BEFORE DELETE ON debts
BEGIN SELECT RAISE(ABORT, 'No se permite eliminar deudas'); END;

CREATE TRIGGER IF NOT EXISTS trg_debt_increases_no_delete
BEFORE DELETE ON debt_increases
BEGIN SELECT RAISE(ABORT, 'No se permite eliminar aumentos de deuda'); END;

CREATE TRIGGER IF NOT EXISTS trg_payments_no_delete
BEFORE DELETE ON payments
BEGIN SELECT RAISE(ABORT, 'No se permite eliminar pagos'); END;
"""


class DB:
    def __init__(self, db_name: str = "fintrack.db"):
        storage_dir = os.getenv("FLET_APP_STORAGE_DATA", "./data")
        os.makedirs(storage_dir, exist_ok=True)
        self.db_path = os.path.join(storage_dir, db_name)
        self._init_db()

    def connect(self) -> sql.Connection:
        conn = sql.connect(self.db_path, isolation_level=None)
        conn.row_factory = sql.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        return conn

    def _init_db(self):
        with self.connect() as conn:
            conn.executescript(SCHEMA)
