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
    transaction_id INTEGER NOT NULL ON DELETE RESTRICT,
    involved_person_id INTEGER NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('PROPIA', 'AJENA')),
    max_repayment_date TEXT,
    settled INTEGER NOT NULL DEFAULT 0 CHECK (settled IN (0, 1)),
    settled_at TEXT,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (involved_person_id) REFERENCES persons(id)   
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    debt_id INTEGER NOT NULL ON DELETE RESTRICT,
    amount INTEGER NOT NULL CHECK (amount > 0),
    method TEXT NOT NULL CHECK (method IN ('EFECTIVO', 'TRANSFERENCIA', 'TARJETA')),
    date TEXT NOT NULL DEFAULT (date('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (debt_id) REFERENCES debts(id)
);

CREATE INDEX IF NOT EXISTS idx_deudas_persona ON deudas(persona_id);
CREATE INDEX IF NOT EXISTS idx_abonos_deuda   ON abonos(deuda_id);
 
CREATE TRIGGER IF NOT EXISTS trg_movimientos_no_delete
BEFORE DELETE ON movimientos
BEGIN SELECT RAISE(ABORT, 'No se permite eliminar movimientos'); END;
 
CREATE TRIGGER IF NOT EXISTS trg_deudas_no_delete
BEFORE DELETE ON deudas
BEGIN SELECT RAISE(ABORT, 'No se permite eliminar deudas'); END;
 
CREATE TRIGGER IF NOT EXISTS trg_abonos_no_delete
BEFORE DELETE ON abonos
BEGIN SELECT RAISE(ABORT, 'No se permite eliminar abonos'); END;

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
