import flet as ft
from services.transaction.TransactionService import TransactionService
from utils.convert import decimal_from_str


class TransactionController:
    def __init__(self, service: TransactionService, page: ft.Page):
        self.service = service
        self.page = page

    def on_save(self, type: str, amount_txt: str, description: str) -> int | None:
        try:
            amount = decimal_from_str(amount_txt)
            transaction_id = self.service.save(type, amount, description)
            self._show_msg("Transaccion registrada correctamente.")
            return transaction_id
        except ValueError as e:
            self._show_msg(str(e), is_error=True)
            return None

    def on_find(self, transaction_id:int):
        try:
            return self.service.find(transaction_id)
        except Exception:
            self._show_msg("Transaccion no encontrada.", is_error=True)
            return None

    def on_find_all(self):
        try:
            return self.service.find_all()
        except Exception:
            self._show_msg("No se pudieron cargar las transacciones")
            return []

    def on_find_by_type(self, type:str):
        try:
            return self.service.find_by_type(type)
        except ValueError as e:
            self._show_msg(str(e), is_error=True)
            return []
        except Exception:
            self._show_msg("No se pudo cargar las transacciones")
            return []

    def _show_msg(self, text: str, is_error: bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(text), bgcolor=ft.Colors.RED if is_error else None
        )
        self.page.snack_bar.open = True
        self.page.update()
