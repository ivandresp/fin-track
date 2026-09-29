import flet as ft
from services.payment.PaymentService import PaymentService

class PaymentController:
    def __init__(self, service:PaymentService, page:ft.Page):
        self.service = service
        self.page = page

    def on_find(self, payment_id:int):
        try:
            return self.service.find(payment_id)
        except Exception:
            self._show_msg("No se encontró el pago", is_error=True)
            return None

    def on_find_all(self):
        try:
            return self.service.find_all()
        except Exception:
            self._show_msg("No se pudo cargar los pagos", is_error=True)
            return []

    def on_find_by_method(self, method:str):
        try:
            return self.service.find_by_method(method)
        except ValueError as e:
            self._show_msg(str(e), is_error=True)
            return []
        except Exception:
            self._show_msg("No se pudo cargar los pagos", is_error=True)
            return []

    def on_find_by_debt(self, debt_id:int):
        try:
            return self.service.find_by_debt(debt_id)
        except Exception:
            self._show_msg("No se pudo cargar los pagos de esta deuda", is_error=True)
            return []

    def _show_msg(self, text:str, is_error:bool = False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(text),
            bgcolor=ft.Colors.RED if is_error else None
        )
        self.page.snack_bar.open = True
        self.page.update()