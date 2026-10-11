import sqlite3 as sql
from models.payment.Payment import Payment, PaymentMethod
from repositories.utils.DB import DB
from repositories.utils.querys import INSERT_PAYMENT, SELECT_PAYMENTS_BY_DEBT, SELECT_PAYMENTS_BY_METHOD, SELECT_ALL_PAYMENTS, SELECT_ONE_PAYMENT

class PaymentRepository:
    def __init__(self, db:DB):
        self.db = db

    def save(self, payment:Payment, conn: sql.Connection) -> int:
        if conn is None:
            with self.db.connect() as c:
                cursor = c.execute(INSERT_PAYMENT, (payment.debt_id, payment.amount, payment.method, payment.date))
        else:
            cursor = conn.execute(INSERT_PAYMENT, (payment.debt_id, payment.amount, payment.method, payment.date))
        return cursor.lastrowid

    def get_by_debt(self, debt_id: int) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(SELECT_PAYMENTS_BY_DEBT, (debt_id,)).fetchall()

    def get_all_by_method(self, method: PaymentMethod) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(SELECT_PAYMENTS_BY_METHOD, (method.value,)).fetchall()

    def get_all(self) -> list[sql.Row]:
        with self.db.connect() as conn:
            return conn.execute(SELECT_ALL_PAYMENTS).fetchall()

    def get(self, payment_id:int) -> sql.Row:
        with self.db.connect() as conn:
            return conn.execute(SELECT_ONE_PAYMENT, (payment_id,)).fetchone()

    