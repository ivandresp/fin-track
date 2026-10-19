from datetime import date

import flet as ft

from controllers.debt.DebtController import DebtController
from controllers.person.PersonController import PersonController
from models.debt.Debt import Debt
from models.debt.DebtIncrease import DebtIncrease
from services.utils.func import to_decimal
from views.ui import (
    DANGER,
    SUCCESS,
    TEXT_MUTED,
    WARNING,
    amount_field,
    badge,
    clean_amount,
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
    tile,
)
from views.welcome import appbar_app


def _is_overdue(debt: Debt) -> bool:
    if debt.settled or not debt.max_repayment_date:
        return False
    try:
        return date.fromisoformat(str(debt.max_repayment_date)[:10]) < date.today()
    except ValueError:
        return False


def _status_badge(debt: Debt) -> ft.Container:
    if debt.settled:
        return badge("Saldada", SUCCESS)
    if _is_overdue(debt):
        return badge("Vencida", DANGER)
    return badge("Pendiente", WARNING)


def _format_increased_at(increased_at) -> str:
    if not increased_at:
        return "Sin fecha"
    if isinstance(increased_at, str):
        return increased_at[:16].replace("T", " ")
    return increased_at.strftime("%Y-%m-%d %H:%M")


def _info_item(label: str, value: str | ft.Control) -> ft.Container:
    content: ft.Control
    if isinstance(value, str):
        content = ft.Text(value, size=14, weight=ft.FontWeight.W_600)
    else:
        content = value
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(label, size=11, color=TEXT_MUTED),
                content,
            ],
            spacing=3,
        )
    )


def debt_detail_view(
    page: ft.Page,
    controller: DebtController,
    person_controller: PersonController,
    user_name: str,
    debt_id: int,
) -> ft.View:
    people_by_id = {p.id: p.name for p in person_controller.on_get_all()}

    hero_slot = ft.Container()
    detail_area = ft.Column(spacing=18)

    def _build_increase_panel(debt: Debt) -> ft.Container:
        if debt.settled:
            return panel(
                ft.Column(
                    [
                        section_title("Aumentar monto"),
                        ft.Text(
                            "Esta deuda está saldada; ya no admite aumentos.",
                            size=13,
                            color=TEXT_MUTED,
                        ),
                    ],
                    spacing=10,
                )
            )

        txt_amount = amount_field(
            "Monto a aumentar", col={"xs": 12, "sm": 6, "md": 4}
        )
        txt_description = text_field(
            "Descripción (opcional)", col={"xs": 12, "sm": 6, "md": 8}
        )

        def _on_increase(_e=None):
            balance = controller.on_increase_amount(
                debt.id,
                clean_amount(txt_amount.value),
                txt_description.value,
            )
            if balance is None:
                page.update()
                return
            _refresh()

        return panel(
            ft.Column(
                [
                    section_title("Aumentar monto"),
                    ft.ResponsiveRow(
                        [txt_amount, txt_description], spacing=12, run_spacing=12
                    ),
                    ft.ResponsiveRow(
                        [
                            primary_button(
                                "Aumentar deuda", _on_increase, ft.Icons.ADD
                            )
                        ]
                    ),
                ],
                spacing=14,
            )
        )

    def _build_history(increases: list[DebtIncrease]) -> ft.Control:
        if not increases:
            return empty_state(
                ft.Icons.HISTORY,
                "Sin aumentos registrados",
                "Cuando aumentes el monto de esta deuda, el registro aparecerá aquí.",
            )

        return grid(
            [
                tile(
                    title=increase.description or "Aumento de deuda",
                    subtitle=f"#{increase.id} · {_format_increased_at(increase.increased_at)}",
                    leading=icon_box(ft.Icons.TRENDING_UP, WARNING),
                    value=f"+{money(to_decimal(increase.amount))}",
                    value_color=WARNING,
                )
                for increase in increases
            ]
        )

    def _render():
        debt = controller.on_find(debt_id)
        if debt is None:
            hero_slot.content = None
            detail_area.controls = [
                empty_state(
                    ft.Icons.MONEY_OFF,
                    "Deuda no encontrada",
                    "Vuelve al listado de deudas e intenta nuevamente.",
                )
            ]
            return

        balance = controller.on_get_balance(debt_id)
        increases = controller.on_find_increases(debt_id)
        person_name = people_by_id.get(debt.involved_person_id, "Desconocido")
        i_owe = debt.direction.value == "PROPIA"
        color = DANGER if i_owe else SUCCESS

        hero_slot.content = hero_card(
            "Saldo pendiente" if not debt.settled else "Deuda saldada",
            money(balance.remaining_amount) if balance else "Sin saldo",
            stats=[
                (
                    "Total",
                    money(balance.total_amount) if balance else "—",
                    ft.Icons.RECEIPT_LONG,
                ),
                (
                    "Pagado",
                    money(balance.total_paid) if balance else "—",
                    ft.Icons.PAYMENTS,
                ),
            ],
        )

        info_items: list[ft.Control] = [
            _info_item("Persona", person_name),
            _info_item("Tipo", "Yo debo" if i_owe else "Me deben"),
            _info_item("Estado", _status_badge(debt)),
            _info_item(
                "Fecha límite",
                str(debt.max_repayment_date)[:10]
                if debt.max_repayment_date
                else "Sin plazo",
            ),
        ]
        info_children: list[ft.Control] = [
            section_title("Información de la deuda"),
            ft.ResponsiveRow(
                [
                    ft.Container(item, col={"xs": 6, "md": 3})
                    for item in info_items
                ],
                spacing=12,
                run_spacing=12,
            ),
        ]
        if balance and balance.total_amount > 0:
            info_children.append(
                ft.Column(
                    [
                        progress_bar(
                            balance.total_paid / balance.total_amount, color
                        ),
                        ft.Text(
                            f"Pagado {money(balance.total_paid)} de "
                            f"{money(balance.total_amount)}",
                            size=11,
                            color=TEXT_MUTED,
                        ),
                    ],
                    spacing=6,
                )
            )

        detail_area.controls = [
            panel(ft.Column(info_children, spacing=14)),
            _build_increase_panel(debt),
            section_title("Historial de aumentos"),
            _build_history(increases),
        ]

    def _refresh():
        _render()
        page.update()

    _render()

    return page_view(
        f"/debts/{debt_id}",
        appbar_app(
            page,
            f"Deuda #{debt_id}",
            user_name,
            back_route="/debts",
        ),
        hero_slot,
        detail_area,
    )
