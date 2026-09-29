import flet as ft

from controllers.payment.PaymentController import PaymentController
from controllers.debt.DebtController import DebtController
from controllers.person.PersonController import PersonController
from models.payment.Payment import Payment
from services.utils.func import to_decimal
from views.welcome import appbar_app

PAYMENT_METHODS = ("EFECTIVO", "TRANSFERENCIA", "TARJETA")

METHOD_ICONS = {
    "EFECTIVO": ft.Icons.PAYMENTS,
    "TRANSFERENCIA": ft.Icons.SWAP_HORIZ,
    "TARJETA": ft.Icons.CREDIT_CARD,
}


def payments_view(page: ft.Page, payment_controller: PaymentController,
    debt_controller: DebtController, person_controller: PersonController,
    user_name: str,
) -> ft.View:
    people_by_id = {p.id: p.name for p in person_controller.on_get_all()}
 
    debt_dropdown = ft.Dropdown(label="Deuda a pagar", width=280)
    method_dropdown = ft.Dropdown(
        label="Método",
        width=180,
        options=[ft.dropdown.Option(m) for m in PAYMENT_METHODS],
        value=PAYMENT_METHODS[0],
    )
    txt_amount = ft.TextField(label="Monto", width=150, keyboard_type=ft.KeyboardType.NUMBER)
    txt_date = ft.TextField(label="Fecha (opcional)", width=150, hint_text="AAAA-MM-DD")
 
    filter_dropdown = ft.Dropdown(
        label="Ver por método",
        width=200,
        options=[ft.dropdown.Option("Todos")] + [ft.dropdown.Option(m) for m in PAYMENT_METHODS],
        value="Todos",
    )
 
    payment_list = ft.ListView(expand=True, spacing=8, padding=10)
 
    def _on_load_unsettled_debts():
        unsettled_debts = debt_controller.on_find_by_settled(False)
        debt_dropdown.options = [
            ft.dropdown.Option(
                key=str(d.id),
                text=f"{people_by_id.get(d.involved_person_id, 'Desconocido')} — deuda #{d.id}",
            )
            for d in unsettled_debts
        ]
        debt_dropdown.value = None
 
    def _refresh_list():
        payment_list.controls.clear()
        if filter_dropdown.value == "Todos":
            payments = payment_controller.on_find_all()
        else:
            payments = payment_controller.on_find_by_method(filter_dropdown.value)
 
        for payment in payments:
            payment_list.controls.append(_row_payment(payment))
        page.update()
 
    def _row_payment(payment:Payment) -> ft.Card:
        debt = debt_controller.buscar(payment.debt_id)
        person_name = (people_by_id.get(debt.involved_person_id, "Desconocido") if debt else "Deuda no encontrada")
        amount = to_decimal(payment.amount)
 
        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Row(
                    [
                        ft.Icon(METHOD_ICONS.get(payment.method.value, ft.Icons.PAYMENT)),
                        ft.Column(
                            [
                                ft.Text(f"${amount}", weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    f"{person_name} — {payment.method.value}",
                                    size=12,
                                    color=ft.Colors.GREY,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Text(str(payment.date), size=12, color=ft.Colors.GREY),
                    ],
                    spacing=10,
                ),
            )
        )
 
    def _on_add(e):
        if not debt_dropdown.value:
            debt_dropdown.error_text = "Selecciona una deuda"
            page.update()
            return
        debt_dropdown.error_text = None
 
        resultado = debt_controller.on_save_payment(
            int(debt_dropdown.value), txt_amount.value,
            method_dropdown.value, txt_date.value or None,
        )
        if resultado is not None:
            txt_amount.value = ""
            txt_date.value = ""
            _on_load_unsettled_debts()  # si quedó saldada, desaparece de la lista
            _refresh_list()
        else:
            page.update()
 
    def _on_filter_change(e):
        _refresh_list()
 
    filter_dropdown.on_change = _on_filter_change
 
    _on_load_unsettled_debts()
    _refresh_list()
 
    return ft.View(
        route="/payments",
        controls=[
            appbar_app("Pagos", user_name),
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [debt_dropdown, method_dropdown, txt_amount, txt_date],
                            wrap=True,
                            spacing=10,
                        ),
                        ft.FilledButton(
                            "Registrar pago", icon=ft.Icons.ADD, on_click=_on_add
                        ),
                        ft.Divider(),
                        filter_dropdown,
                        payment_list,
                    ],
                    spacing=15,
                    expand=True,
                ),
            ),
        ],
    )
