import sqlite3 as sql

from models.debt.DebtIncrease import DebtIncrease
from repositories.utils.DB import DB
from repositories.utils.querys import (
    INSERT_DEBT_INCREASE,
    SELECT_ALL_DEBT_INCREASES,
    SELECT_DEBT_INCREASES_BY_DEBT,
    SELECT_ONE_DEBT_INCREASE,
)


class DebtIncreaseRepository:
    def __init__(self, db: DB):
        self.db = db

    def save(
        self, increase: DebtIncrease, conn: sql.Connection | None = None
    ) -> int:
        params = (increase.debt_id, increase.amount, increase.description)
        if conn is None:
            with self.db.connect() as c:
                return c.execute(INSERT_DEBT_INCREASE, params).lastrowid

        return conn.execute(INSERT_DEBT_INCREASE, params).lastrowid

    def get_by_debt(self, debt_id: int) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(SELECT_DEBT_INCREASES_BY_DEBT, (debt_id,)).fetchall()

    def get_all(self) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(SELECT_ALL_DEBT_INCREASES).fetchall()

    def get(self, increase_id: int) -> sql.Row:
        with self.db.connect() as conn:
            return conn.execute(SELECT_ONE_DEBT_INCREASE, (increase_id,)).fetchone()
