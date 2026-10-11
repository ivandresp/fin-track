SELECT_ALL_PEOPLE = "SELECT * FROM persons ORDER BY name"
INSERT_PERSON = "INSERT INTO persons (name, phone) VALUES (?, ?)"

INSERT_TRANSACTION = "INSERT INTO transactions (type, amount, description) VALUES (?, ?, ?)"
SELECT_ALL_TRANSACTIONS = "SELECT * FROM transactions ORDER BY date DESC"
SELECT_TRANSACTION_BY_TYPE = "SELECT * FROM transactions WHERE type = ? ORDER BY date DESC"
SELECT_ONE_TRANSACTION = "SELECT * FROM transactions WHERE id = ?"

INSERT_DEBT = "INSERT INTO debts (transaction_id, involved_person_id, direction, max_repayment_date) VALUES (?, ?, ?, ?)"
SELECT_ALL_DEBTS = "SELECT * FROM debts"
SELECT_DEBTS_BY_PERSON = "SELECT * FROM debts WHERE involved_person_id = ?"
SELECT_DEBTS_BY_SETTLEMENT_STATUS = "SELECT * FROM debts WHERE settled = ?"
SELECT_ONE_DEBT = "SELECT * FROM debts WHERE id = ?"
SELECT_DEBTS_BY_DIRECTION = "SELECT * FROM debts WHERE direction = ?"

SELECT_DEBT_TOTAL = """
    SELECT t.amount AS total_amount, COALESCE(SUM(p.amount), 0) AS total_paid, (t.amount - COALESCE(SUM(p.amount), 0)) AS remaining_amount
    FROM debts d
    JOIN transactions t ON d.transaction_id = t.id
    LEFT JOIN payments p ON d.id = p.debt_id
    WHERE d.id = ?
    GROUP BY d.id
"""

SETTLE_DEBT = "UPDATE debts SET settled = 1, settled_at = datetime('now') WHERE id = ?"

INSERT_PAYMENT = "INSERT INTO payments (debt_id, amount, method, date) VALUES (?, ?, ?, ?)"
SELECT_ALL_PAYMENTS = "SELECT * FROM payments ORDER BY date DESC"
SELECT_PAYMENTS_BY_DEBT = "SELECT * FROM payments WHERE debt_id = ? ORDER BY date DESC"
SELECT_PAYMENTS_BY_METHOD = "SELECT * FROM payments WHERE method = ? ORDER BY date DESC"
SELECT_ONE_PAYMENT = "SELECT * FROM payments WHERE id = ?"