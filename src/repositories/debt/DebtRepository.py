import sqlite3 as sql
from repositories.utils.querys import (
    INSERT_DEBT,
    SELECT_ALL_DEBTS,
    SELECT_DEBTS_BY_PERSON,
    SELECT_DEBTS_BY_SETTLEMENT_STATUS,
    SELECT_DEBT_TOTAL,
    SETTLE_DEBT,
    SELECT_ONE_DEBT,
    SELECT_DEBTS_BY_DIRECTION
)
from models.debt.Debt import Debt
from models.debt.DebtDirection import DebtDirection
from models.payment.Payment import Payment
from repositories.utils.DB import DB
from repositories.payment.PaymentRepository import PaymentRepository


class DebtRepository:
    def __init__(self, db: DB, payment_repository: PaymentRepository | None = None):
        self.db = db
        self.payment_repository = payment_repository

    def save(self, debt: Debt) -> int:
        with self.db.connect() as conn:
            cursor = conn.execute(
                INSERT_DEBT,
                (
                    debt.transaction_id,
                    debt.involved_person_id,
                    debt.direction,
                    debt.max_repayment_date,
                ),
            )
            return cursor.lastrowid

    def get_all(self) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(SELECT_ALL_DEBTS).fetchall()

    def get_by_person(self, person_id: int) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(SELECT_DEBTS_BY_PERSON, (person_id,)).fetchall()

    def get_by_settlement_status(self, settled: bool) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(
                SELECT_DEBTS_BY_SETTLEMENT_STATUS, (int(settled),)
            ).fetchall()

    def get_debt_total(self, debt_id: int, conn: sql.Connection | None) -> sql.Row:
        if conn is None:
            with self.db.connect() as conn:
                return conn.execute(SELECT_DEBT_TOTAL, (debt_id,)).fetchone()

        return conn.execute(SELECT_DEBT_TOTAL, (debt_id,)).fetchone()

    def get(self, debt_id: int) -> sql.Row:
        with self.db.connect() as conn:
            return conn.execute(SELECT_ONE_DEBT, (debt_id,)).fetchone()

    def register_payment_and_validate(self, payment: Payment) -> tuple[int, bool]:
        conn = self.db.connect()
        try:
            conn.execute("BEGIN INMEDIATE")

            p_id = self.payment_repository.save(payment, conn=conn)

            row = self.get_debt_total(payment.debt_id, conn)

            if row is None:
                raise ValueError(f"No existe la deuda {payment.debt_id}")

            settled = row["remaining_amount"] == 0
            if settled:
                conn.execute(SETTLE_DEBT, (payment.debt_id,))

            conn.commit()
            return (p_id, settled)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_by_direction(self, direction: DebtDirection):
        with self.db.connect() as conn:
            return conn.execute(SELECT_DEBTS_BY_DIRECTION, (direction.value,)).fetchall()
