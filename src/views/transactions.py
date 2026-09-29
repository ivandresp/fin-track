import flet as ft

from controller.transaction.TransactionController import TransactionController
from services.utils.func import to_decimal
from models.transaction.Transaction import Transaction
from views.welcome import appbar_app

CREABLE_TYPES = ("GASTO", "INGRESO")

TYPES_ICONS = {
    "GASTO":(ft.Icons.ARROW_UPWARD, ft.Colors.RED),
    "INGRESO":(ft.Icons.ARROW_DOWNWARD, ft.Colors.GREEN),
    "DEUDA":(ft.Icons.SWAP_HORIZ, ft.Colors.ORANGE),
}

def transactions_view(page:ft.Page, controller: TransactionController, user_name:str) -> ft.View:
    dropdown_type = ft.Dropdown(
        label="Tipo",
        width=200,
        options=[ft.dropdown.Option(t) for t in CREABLE_TYPES],
        value=CREABLE_TYPES[0],
    )
    txt_amount = ft.TextField(label="Monto",width=150, keyboard_type=ft.KeyboardType.NUMBER)
    txt_desc = ft.TextField(label="Descripcion", width=300)

    transactions = ft.ListView(expand=True, spacing=8, padding=10)

    def _refresh():
        transactions.controls.clear()
        for trans in controller.on_find_all():
            transactions.controls.append(_row_transaction(trans))
        page.update()

    def _row_transaction(transaction:Transaction) -> ft.Card:
        icon, color = TYPES_ICONS.get(transaction.type.value, (ft.Icons.HELP, ft.Colors.GREY))
        amount = to_decimal(transaction.amount)
        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Row(
                    [
                        ft.Icon(icon, color=color),
                        ft.Column(
                            [
                                ft.Text(transaction.description, weight=ft.FontWeight.BOLD),
                                ft.Text(transaction.type.value, size=12, color=ft.Colors.GREY),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Text(f"{amount}", weight=ft.FontWeight.BOLD, color=color),
                    ],
                    spacing=10,
                ),
            )
        )

    def _on_add(e):
        trans_id = controller.on_save(dropdown_type.value, txt_amount.value, txt_desc.value)
        if trans_id is not None:
            txt_amount.value = ""
            txt_desc.value = ""
            _refresh()
        else:
            page.update()

    _refresh()

    return ft.View(
        route="/transactions",
        controls=[
            appbar_app("Transacciones", user_name),
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [dropdown_type, txt_amount, txt_desc],
                            wrap=True,
                            spacing=10,
                        ),
                        ft.FilledButton(
                            "Agregar transacción", icon=ft.Icons.ADD, on_click=_on_add
                        ),
                        ft.Divider(),
                        transactions,
                    ],
                    spacing=15,
                    expand=True,
                ),
            ),
        ],
    )

