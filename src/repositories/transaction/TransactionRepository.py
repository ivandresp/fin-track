import sqlite3 as sql
from repositories.utils.querys import (
    INSERT_TRANSACTION,
    SELECT_ALL_TRANSACTIONS,
    SELECT_TRANSACTION_BY_TYPE,
    SELECT_ONE_TRANSACTION
)
from models.transaction.Transaction import Transaction
from repositories.utils.DB import DB


class TransactionRepository:
    def __init__(self, db: DB):
        self.db = db

    def save(self, transaction: Transaction) -> int:
        with self.db.connect() as conn:
            cursor = conn.execute(
                INSERT_TRANSACTION,
                (transaction.type, transaction.amount, transaction.description),
            )
            return cursor.lastrowid

    def get_all(self) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(SELECT_ALL_TRANSACTIONS).fetchall()

    def get_by_type(self, transaction_type: str) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(
                SELECT_TRANSACTION_BY_TYPE, (transaction_type,)
            ).fetchall()

    def get(self, transaction_id: int) -> sql.Row:
        with self.db.connect() as conn:
            return conn.execute(SELECT_ONE_TRANSACTION, (transaction_id,)).fetchone()
