import flet as ft
from services.debt.DebtService import DebtService
from utils.convert import decimal_from_str

class DebtController:
    def __init__(self, service: DebtService, page:ft.Page):
        self.service = service
        self.page = page

    def on_save(self, transaction_id:int, involved_person_id:int, direction:str, max_repayment_date:str | None):
        try:
            return self.service.save(transaction_id, involved_person_id, direction, max_repayment_date)
        except (ValueError, TypeError) as e:
            msg = str(e) if isinstance(e, ValueError) else "La fecha es invalida"
            self._show_msg(msg, is_error=True)
            return None

    def on_find(self, debt_id:int):
        try:
            return self.service.find(debt_id)
        except Exception:
            self._show_msg("No se encontro la deuda", is_error=True)
            return None

    def on_find_all(self):
        try:
            return self.service.find_all()
        except Exception:
            self._show_msg("No se pudieron cargar las deudas", is_error=True)
            return []

    def on_find_by_person(self, person_id:int):
        try:
            return self.service.find_by_person(person_id)
        except Exception:
            self._show_msg("No se pudieron cargar las deudas de esta persona", is_error=True)
            return []

    def on_find_by_settled(self, is_settled:bool):
        try:
            return self.service.find_by_settled(is_settled)
        except Exception:
            self._show_msg("No se pudieron cargar las deudas", is_error=True)
            return []

    def on_get_balance(self, debt_id:int):
        try:
            return self.service.find_debt_balance(debt_id)
        except Exception:
            self._show_msg("No se pudo calcular el saldo de la deuda.", is_error=True)
            return None

    def on_save_payment(self, debt_id:int, amount_txt:str, method:str, date:str | None):
        try:
            amount = decimal_from_str(amount_txt)
            payment_id, settled = self.service.add_payment_to_debt(debt_id, amount, method, date)
            msg = "¡Deuda Saldada!" if settled else "Pago Registrado"
            self._show_msg(msg)
            return payment_id, settled
        except ValueError as e:
            self._show_msg(str(e), is_error=True)
            return None 

    def on_find_by_direction(self, direction:str):
        try:
            return self.service.find_by_direction(direction)
        except ValueError as e:
            self._show_msg(str(e), is_error=True)
            return []
        except Exception:
            self._show_msg(f"No se pudieron cargar las deudas '{direction}'.")
            return []

    def _show_msg(self, text:str, is_error:bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=ft.Colors.RED if is_error else None
        )
        self.page.snack_bar.open = True
        self.page.update()