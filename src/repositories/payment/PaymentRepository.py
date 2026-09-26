import sqlite3 as sql
from models.payment.Payment import Payment
from repositories.utils.DB import DB
from repositories.utils.querys import INSERT_PAYMENT, SELECT_PAYMENTS_BY_DEBT, SELECT_PAYMENTS_BY_METHOD, SELECT_ALL_PAYMENTS

class PaymentRepository:
    def __init__(self, db:DB):
        self.db = db

    def save(self, payment:Payment, conn: sql.Connection) -> int:
        conn = conn if conn is not None else self.db.connect()
        cursor = conn.execute(INSERT_PAYMENT, (payment.debt_id, payment.amount, payment.method, payment.date))
        conn.close()
        return cursor.lastrowid

    

        
