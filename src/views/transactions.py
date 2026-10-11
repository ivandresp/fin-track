import flet as ft

from controllers.transaction.TransactionController import TransactionController
from services.utils.func import to_decimal
from models.transaction.Transaction import Transaction
from views.ui import (
    ACCENT,
    DANGER,
    SUCCESS,
    WARNING,
    PillSelector,
    amount_field,
    clean_amount,
    dropdown,
    empty_state,
    grid,
    hero_card,
    icon_box,
    money,
    page_view,
    panel,
    primary_button,
    section_title,
    text_field,
    tile,
)
from views.welcome import appbar_app

CREABLE_TYPES = ("GASTO", "INGRESO")

# tipo: (icono, color, etiqueta, signo)
TYPE_STYLE = {
    "GASTO": (ft.Icons.ARROW_UPWARD, DANGER, "Gasto", "-"),
    "INGRESO": (ft.Icons.ARROW_DOWNWARD, SUCCESS, "Ingreso", "+"),
    "DEUDA": (ft.Icons.SWAP_HORIZ, WARNING, "Deuda", ""),
}

FILTER_OPTIONS = [
    ("ALL", "Todas"),
    ("INGRESO", "Ingresos"),
    ("GASTO", "Gastos"),
    ("DEUDA", "Deudas"),
]


def transactions_view(
    page: ft.Page, controller: TransactionController, user_name: str
) -> ft.View:
    dropdown_type = dropdown(
        "Tipo",
        options=[
            ft.dropdown.Option(key="GASTO", text="Gasto"),
            ft.dropdown.Option(key="INGRESO", text="Ingreso"),
        ],
        value=CREABLE_TYPES[0],
        col={"xs": 12, "sm": 6, "md": 3},
    )
    txt_amount = amount_field(col={"xs": 12, "sm": 6, "md": 3})
    txt_desc = text_field("Descripción", col={"xs": 12, "md": 6})

    hero_slot = ft.Container()
    list_area = ft.Column(spacing=12)

    def _row_transaction(transaction: Transaction) -> ft.Container:
        kind = transaction.type.value
        icon, color, label, sign = TYPE_STYLE.get(
            kind, (ft.Icons.HELP, ACCENT, kind.title(), "")
        )
        date = getattr(transaction, "date", None)
        subtitle = f"{label}, {str(date)[:10]}" if date else label
        return tile(
            title=transaction.description or label,
            subtitle=subtitle,
            leading=icon_box(icon, color),
            value=f"{sign}{money(to_decimal(transaction.amount))}",
            value_color=color,
        )

    def _render():
        everything = controller.on_find_all()

        income = sum(
            (to_decimal(t.amount) for t in everything if t.type.value == "INGRESO"), 0
        )
        expenses = sum(
            (to_decimal(t.amount) for t in everything if t.type.value == "GASTO"), 0
        )
        hero_slot.content = hero_card(
            "Balance total",
            money(income - expenses),
            stats=[
                ("Ingresos", money(income), ft.Icons.ARROW_DOWNWARD),
                ("Gastos", money(expenses), ft.Icons.ARROW_UPWARD),
            ],
        )

        selected = filters.value
        shown = (
            everything
            if selected == "ALL"
            else [t for t in everything if t.type.value == selected]
        )
        if shown:
            list_area.controls = [grid([_row_transaction(t) for t in shown])]
        else:
            list_area.controls = [
                empty_state(
                    ft.Icons.RECEIPT_LONG,
                    "No hay movimientos aquí",
                    "Registra un ingreso o un gasto con el formulario de arriba.",
                )
            ]

    def _refresh():
        _render()
        page.update()

    filters = PillSelector(FILTER_OPTIONS, "ALL", lambda _key: _refresh())

    def _on_add(e):
        trans_id = controller.on_save(
            dropdown_type.value, clean_amount(txt_amount.value), txt_desc.value
        )
        if trans_id is not None:
            txt_amount.value = ""
            txt_desc.value = ""
            _refresh()
        else:
            page.update()

    _render()

    form = panel(
        ft.Column(
            [
                section_title("Nuevo movimiento"),
                ft.ResponsiveRow(
                    [dropdown_type, txt_amount, txt_desc], spacing=12, run_spacing=12
                ),
                ft.ResponsiveRow(
                    [primary_button("Guardar movimiento", _on_add, ft.Icons.ADD)]
                ),
            ],
            spacing=14,
        )
    )

    return page_view(
        "/transactions",
        appbar_app(page, "Transacciones", user_name),
        hero_slot,
        form,
        section_title("Movimientos"),
        filters.control,
        list_area,
    )
