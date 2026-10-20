import sqlite3 as sql
from repositories.utils.querys import (
    INSERT_DEBT,
    SELECT_ALL_DEBTS,
    SELECT_DEBTS_BY_PERSON,
    SELECT_DEBTS_BY_SETTLEMENT_STATUS,
    SELECT_DEBT_TOTAL,
    SETTLE_DEBT,
    SELECT_ONE_DEBT,
    SELECT_DEBTS_BY_DIRECTION,
    INCREASE_DEBT_AMOUNT,
)
from models.debt.Debt import Debt
from models.debt.DebtDirection import DebtDirection
from models.debt.DebtIncrease import DebtIncrease
from models.payment.Payment import Payment
from repositories.utils.DB import DB
from repositories.debt.DebtIncreaseRepository import DebtIncreaseRepository
from repositories.payment.PaymentRepository import PaymentRepository


class DebtRepository:
    def __init__(
        self,
        db: DB,
        payment_repository: PaymentRepository | None = None,
        debt_increase_repository: DebtIncreaseRepository | None = None,
    ):
        self.db = db
        self.payment_repository = payment_repository
        self.debt_increase_repository = (
            debt_increase_repository or DebtIncreaseRepository(db)
        )

    def save(self, debt: Debt) -> int:
        max_repayment_date = (
            debt.max_repayment_date.isoformat()
            if debt.max_repayment_date
            else None
        )
        with self.db.connect() as conn:
            cursor = conn.execute(
                INSERT_DEBT,
                (
                    debt.transaction_id,
                    debt.involved_person_id,
                    debt.direction,
                    max_repayment_date,
                ),
            )
            return cursor.lastrowid

    def increase_amount(self, increase: DebtIncrease) -> sql.Row:
        """Aplica un aumento y guarda su historial en una sola transacción.

        Retorna la fila con los totales actualizados. La condición ``settled = 0``
        vive dentro del UPDATE para que la validación sea atómica.
        """
        conn = self.db.connect()
        try:
            conn.execute("BEGIN IMMEDIATE")

            cursor = conn.execute(
                INCREASE_DEBT_AMOUNT, (increase.amount, increase.debt_id)
            )
            if cursor.rowcount == 0:
                raise ValueError(
                    f"No existe la deuda {increase.debt_id} o ya está saldada."
                )

            self.debt_increase_repository.save(increase, conn=conn)
            row = self.get_debt_total(increase.debt_id, conn)

            conn.commit()
            return row
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

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
            conn.execute("BEGIN IMMEDIATE")

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
