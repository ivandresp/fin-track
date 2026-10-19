from datetime import date
from decimal import Decimal

import flet as ft

from controllers.debt.DebtController import DebtController
from controllers.person.PersonController import PersonController
from models.debt.Debt import Debt
from views.ui import (
    DANGER,
    SUCCESS,
    TEXT_MUTED,
    WARNING,
    PillSelector,
    amount_field,
    clean_amount,
    badge,
    dropdown,
    empty_state,
    grid,
    hero_card,
    icon_box,
    money,
    page_view,
    panel,
    primary_button,
    progress_bar,
    section_title,
    text_field,
)
from views.ui import tile
from views.welcome import appbar_app

# Filtros: clave -> etiqueta. PROPIA = yo debo, AJENA = me deben.
FILTER_OPTIONS = [
    ("ALL", "Todas"),
    ("PROPIA", "Yo debo"),
    ("AJENA", "Me deben"),
    ("PENDING", "Pendientes"),
    ("SETTLED", "Saldadas"),
]


def _is_overdue(debt: Debt) -> bool:
    if debt.settled or not debt.max_repayment_date:
        return False
    try:
        return date.fromisoformat(str(debt.max_repayment_date)[:10]) < date.today()
    except ValueError:
        return False


def debts_view(
    page: ft.Page,
    controller: DebtController,
    person_controller: PersonController,
    user_name: str,
) -> ft.View:
    people = person_controller.on_get_all()
    people_by_id = {p.id: p.name for p in people}

    dropdown_people = dropdown(
        "Persona",
        options=[ft.dropdown.Option(key=str(p.id), text=p.name) for p in people],
        col={"xs": 12, "sm": 6, "md": 4},
    )
    if not people:
        dropdown_people.helper = "Primero registra una persona"

    dropdown_direction = dropdown(
        "Tipo de deuda",
        options=[
            ft.dropdown.Option(key="PROPIA", text="Yo debo"),
            ft.dropdown.Option(key="AJENA", text="Me deben"),
        ],
        value="PROPIA",
        col={"xs": 12, "sm": 6, "md": 4},
    )
    txt_amount = amount_field(col={"xs": 12, "sm": 6, "md": 4})
    txt_desc = text_field("Descripción", col={"xs": 12, "sm": 6, "md": 6})
    txt_max_date = text_field(
        "Plazo máximo (opcional)",
        hint_text="AAAA-MM-DD",
        col={"xs": 12, "sm": 6, "md": 6},
    )

    hero_slot = ft.Container()
    list_area = ft.Column(spacing=12)

    def _open_increase_dialog(debt: Debt, balance):
        person_name = people_by_id.get(debt.involved_person_id, "Desconocido")
        current_remaining = balance.remaining_amount if balance else None
        txt_increase = amount_field("Monto a aumentar", autofocus=True)

        def _close(_e=None):
            page.pop_dialog()

        def _confirm(_e=None):
            updated = controller.on_increase_amount(
                debt.id, clean_amount(txt_increase.value)
            )
            if updated is None:
                return
            dialog.open = False
            dialog.update()
            _refresh()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Aumentar deuda"),
            content=ft.Column(
                [
                    ft.Text(
                        f"{person_name} · "
                        f"{'Yo debo' if debt.direction.value == 'PROPIA' else 'Me deben'}",
                        size=13,
                        color=TEXT_MUTED,
                    ),
                    ft.Text(
                        f"Saldo actual: {money(current_remaining)}"
                        if current_remaining is not None
                        else "Saldo no disponible",
                        size=13,
                        color=TEXT_MUTED,
                    ),
                    txt_increase,
                ],
                tight=True,
                spacing=12,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=_close),
                ft.FilledButton("Aumentar", on_click=_confirm),
            ],
        )
        page.show_dialog(dialog)

    def _row_debt(debt: Debt, balance) -> ft.Container:
        person_name = people_by_id.get(debt.involved_person_id, "Desconocido")
        i_owe = debt.direction.value == "PROPIA"
        color = DANGER if i_owe else SUCCESS

        subtitle = "Yo debo" if i_owe else "Me deben"
        if debt.max_repayment_date:
            subtitle += f", vence {str(debt.max_repayment_date)[:10]}"

        if debt.settled:
            status = badge("Saldada", SUCCESS)
        elif _is_overdue(debt):
            status = badge("Vencida", DANGER)
        else:
            status = badge("Pendiente", WARNING)

        aside = status
        if not debt.settled:
            aside = ft.Row(
                [
                    status,
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                        icon_color=color,
                        icon_size=20,
                        tooltip="Aumentar monto",
                        on_click=lambda e, d=debt, b=balance: _open_increase_dialog(
                            d, b
                        ),
                    ),
                ],
                spacing=2,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )

        remaining = balance.remaining_amount if balance else None

        footer = None
        total_cents = getattr(balance, "total_amount", None) if balance else None
        if balance and total_cents:
            paid_cents = total_cents - balance.remaining_amount
            footer = ft.Column(
                [
                    progress_bar(paid_cents / total_cents, color),
                    ft.Text(
                        f"Pagado {money(paid_cents)} de " f"{money(total_cents)}",
                        size=11,
                        color=TEXT_MUTED,
                    ),
                ],
                spacing=6,
            )

        return tile(
            title=person_name,
            subtitle=subtitle,
            leading=icon_box(
                ft.Icons.ARROW_UPWARD if i_owe else ft.Icons.ARROW_DOWNWARD, color
            ),
            value=money(remaining) if remaining is not None else "Sin saldo",
            value_color=TEXT_MUTED if debt.settled else color,
            aside=aside,
            footer=footer,
        )

    def _render():
        pending = controller.on_find_by_settled(False)
        balances = {d.id: controller.on_get_balance(d.id) for d in pending}

        owed_to_me = Decimal(0)
        i_owe_total = Decimal(0)
        for d in pending:
            b = balances.get(d.id)
            if not b:
                continue
            remaining = b.remaining_amount
            if d.direction.value == "AJENA":
                owed_to_me += remaining
            else:
                i_owe_total += remaining

        hero_slot.content = hero_card(
            "Balance de deudas",
            money(owed_to_me - i_owe_total),
            stats=[
                ("Me deben", money(owed_to_me), ft.Icons.ARROW_DOWNWARD),
                ("Yo debo", money(i_owe_total), ft.Icons.ARROW_UPWARD),
            ],
        )

        selected = filters.value
        if selected == "ALL":
            debts = controller.on_find_all()
        elif selected in ("PROPIA", "AJENA"):
            debts = controller.on_find_by_direction(selected)
        elif selected == "PENDING":
            debts = pending
        else:
            debts = controller.on_find_by_settled(True)

        if debts:
            list_area.controls = [
                grid(
                    [
                        _row_debt(
                            d, balances.get(d.id) or controller.on_get_balance(d.id)
                        )
                        for d in debts
                    ]
                )
            ]
        else:
            list_area.controls = [
                empty_state(
                    ft.Icons.MONEY_OFF,
                    "No hay deudas en esta vista",
                    "Registra una deuda con el formulario de arriba o cambia el filtro.",
                )
            ]

    def _refresh():
        _render()
        page.update()

    filters = PillSelector(FILTER_OPTIONS, "ALL", lambda _key: _refresh())

    def _on_add(e):
        if not dropdown_people.value:
            dropdown_people.error = "Selecciona una persona"
            page.update()
            return
        dropdown_people.error = None

        debt_id = controller.on_save_complete(
            clean_amount(txt_amount.value),
            txt_desc.value,
            int(dropdown_people.value),
            dropdown_direction.value,
            txt_max_date.value or None,
        )
        if debt_id is not None:
            txt_amount.value = ""
            txt_desc.value = ""
            txt_max_date.value = ""
            _refresh()
        else:
            page.update()

    _render()

    form = panel(
        ft.Column(
            [
                section_title("Nueva deuda"),
                ft.ResponsiveRow(
                    [dropdown_people, dropdown_direction, txt_amount],
                    spacing=12,
                    run_spacing=12,
                ),
                ft.ResponsiveRow([txt_desc, txt_max_date], spacing=12, run_spacing=12),
                ft.ResponsiveRow(
                    [primary_button("Guardar deuda", _on_add, ft.Icons.ADD)]
                ),
            ],
            spacing=14,
        )
    )

    return page_view(
        "/debts",
        appbar_app(page, "Deudas", user_name),
        hero_slot,
        form,
        section_title("Tus deudas"),
        filters.control,
        list_area,
    )
