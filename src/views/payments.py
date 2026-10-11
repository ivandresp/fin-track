import flet as ft

from controllers.payment.PaymentController import PaymentController
from controllers.debt.DebtController import DebtController
from controllers.person.PersonController import PersonController
from models.payment.Payment import Payment
from services.utils.func import to_decimal
from views.ui import (
    ACCENT,
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

PAYMENT_METHODS = ("EFECTIVO", "TRANSFERENCIA", "TARJETA")

METHOD_LABELS = {
    "EFECTIVO": "Efectivo",
    "TRANSFERENCIA": "Transferencia",
    "TARJETA": "Tarjeta",
}

METHOD_ICONS = {
    "EFECTIVO": ft.Icons.PAYMENTS,
    "TRANSFERENCIA": ft.Icons.SWAP_HORIZ,
    "TARJETA": ft.Icons.CREDIT_CARD,
}

FILTER_OPTIONS = [("ALL", "Todos")] + [(m, METHOD_LABELS[m]) for m in PAYMENT_METHODS]


def payments_view(
    page: ft.Page,
    payment_controller: PaymentController,
    debt_controller: DebtController,
    person_controller: PersonController,
    user_name: str,
) -> ft.View:
    people_by_id = {p.id: p.name for p in person_controller.on_get_all()}

    debt_dropdown = dropdown("Deuda a pagar", options=[], col={"xs": 12, "md": 6})
    method_dropdown = dropdown(
        "Método",
        options=[
            ft.dropdown.Option(key=m, text=METHOD_LABELS[m]) for m in PAYMENT_METHODS
        ],
        value=PAYMENT_METHODS[0],
        col={"xs": 12, "sm": 6, "md": 3},
    )
    txt_amount = amount_field(col={"xs": 12, "sm": 6, "md": 3})
    txt_date = text_field(
        "Fecha (opcional)", hint_text="AAAA-MM-DD", col={"xs": 12, "sm": 6, "md": 4}
    )

    hero_slot = ft.Container()
    list_area = ft.Column(spacing=12)
    state = {"pending_count": 0}

    def _load_unsettled_debts():
        unsettled = debt_controller.on_find_by_settled(False)
        state["pending_count"] = len(unsettled)

        options = []
        for d in unsettled:
            name = people_by_id.get(d.involved_person_id, "Desconocido")
            balance = debt_controller.on_get_balance(d.id)
            detail = (
                f"restan {money(balance.remaining_amount)}"
                if balance
                else f"deuda #{d.id}"
            )
            options.append(ft.dropdown.Option(key=str(d.id), text=f"{name} ({detail})"))
        debt_dropdown.options = options
        debt_dropdown.value = None
        debt_dropdown.helper = None if options else "No tienes deudas pendientes"

    def _row_payment(payment: Payment) -> ft.Container:
        debt = debt_controller.on_find(payment.debt_id)
        person_name = (
            people_by_id.get(debt.involved_person_id, "Desconocido")
            if debt
            else "Deuda no encontrada"
        )
        method = payment.method.value
        return tile(
            title=person_name,
            subtitle=METHOD_LABELS.get(method, method.title()),
            leading=icon_box(METHOD_ICONS.get(method, ft.Icons.PAYMENT), ACCENT),
            value=money(to_decimal(payment.amount)),
            aside=str(payment.date)[:10],
        )

    def _render():
        selected = filters.value
        if selected == "ALL":
            payments = payment_controller.on_find_all()
        else:
            payments = payment_controller.on_find_by_method(selected)

        total = sum((to_decimal(p.amount) for p in payments), 0)
        hero_slot.content = hero_card(
            "Total pagado",
            money(total),
            stats=[
                ("Pagos", str(len(payments)), ft.Icons.RECEIPT_LONG),
                (
                    "Deudas pendientes",
                    str(state["pending_count"]),
                    ft.Icons.PENDING_ACTIONS,
                ),
            ],
        )

        if payments:
            list_area.controls = [grid([_row_payment(p) for p in payments])]
        else:
            list_area.controls = [
                empty_state(
                    ft.Icons.PAYMENTS,
                    "Todavía no hay pagos",
                    "Elige una deuda y registra tu primer abono.",
                )
            ]

    def _refresh():
        _render()
        page.update()

    filters = PillSelector(FILTER_OPTIONS, "ALL", lambda _key: _refresh())

    def _on_add(e):
        if not debt_dropdown.value:
            debt_dropdown.error = "Selecciona una deuda"
            page.update()
            return
        debt_dropdown.error = None

        result = debt_controller.on_save_payment(
            int(debt_dropdown.value),
            clean_amount(txt_amount.value),
            method_dropdown.value,
            txt_date.value or None,
        )
        if result is not None:
            txt_amount.value = ""
            txt_date.value = ""
            _load_unsettled_debts()  # si quedó saldada, desaparece de la lista
            _refresh()
        else:
            page.update()

    _load_unsettled_debts()
    _render()

    form = panel(
        ft.Column(
            [
                section_title("Nuevo pago"),
                ft.ResponsiveRow(
                    [debt_dropdown, method_dropdown, txt_amount],
                    spacing=12,
                    run_spacing=12,
                ),
                ft.ResponsiveRow([txt_date], spacing=12, run_spacing=12),
                ft.ResponsiveRow(
                    [primary_button("Registrar pago", _on_add, ft.Icons.ADD)]
                ),
            ],
            spacing=14,
        )
    )

    return page_view(
        "/payments",
        appbar_app(page, "Pagos", user_name),
        hero_slot,
        form,
        section_title("Historial de pagos"),
        filters.control,
        list_area,
    )
