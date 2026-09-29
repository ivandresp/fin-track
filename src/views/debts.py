import flet as ft

from controllers.debt.DebtController import DebtController
from controllers.person.PersonController import PersonController
from views.welcome import appbar_app
from models.debt.Debt import Debt

DIRECTIONS = ("PROPIA", "AJENA")

FILTERS = {
    "Todas":None,
    "Propias": ("direction", "PROPIA"),
    "Ajenas": ("direction", "AJENA"),
    "Pendientes": ("settled", False),
    "Saldadas": ("settled", True),
}

def debts_view(page: ft.Page, controller:DebtController, person_controller:PersonController, user_name:str) -> ft.View:
    people = person_controller.on_get_all()
    people_by_id = {p.id: p.name for p in people}

    dropdown_people = ft.Dropdown(
        label="Persona", width=220,
        options=[ft.dropdown.Option(key=str(p.id), text=p.name) for p in people],
    )
    dropdown_direction = ft.Dropdown(
        label="Direccion", width=150,
        options=[ft.dropdown.Option(d) for d in DIRECTIONS],
        value=DIRECTIONS[0],
    )
    txt_amount = ft.TextField(label="Monto", width=130, keyboard_type=ft.KeyboardType.NUMBER)
    txt_desc = ft.TextField(label="Descripción", width=250)
    txt_max_date = ft.TextField(
        label="Plazo máximo (opcional)", width=200, hint_text="AAAA-MM-DD",
    )

    dropdown_filter = ft.Dropdown(
        label="Ver",
        width=180,
        options=[ft.dropdown.Option(f) for f in FILTERS.keys()],
        value="Todas",
    )

    debts_list = ft.ListView(expand=True, spacing=8, padding=10)

    def _refresh():
        debts_list.controls.clear()
        filter = FILTERS[dropdown_filter.value]
        
        if filter is None:
            debts = controller.on_find_all()
        elif filter[0] == "direction":
            debts = controller.on_find_by_direction(filter[1])
        else:
            debts = controller.on_find_by_settled(filter[1])

        for debt in debts:
            debts_list.controls.append(_row_debt(debt))

        page.update()

    def _row_debt(debt:Debt) -> ft.Card:
        person_name = people_by_id.get(debt.involved_person_id, "Desconocido")
        is_propia = debt.direction.value == "PROPIA"
        color = ft.Colors.RED if is_propia else ft.Colors.GREEN
        icon = ft.Icons.ARROW_UPWARD if is_propia else ft.Icons.ARROW_DOWNWARD

        balance = controller.on_get_balance(debt.id)
        saldo_text = f"Restante: ${balance.remaining_amount}" if balance else "Saldo no disponible"

        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Row(
                    [
                        ft.Icon(icon, color=color),
                        ft.Column(
                            [
                                ft.Text(person_name, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    "Le debes" if is_propia else "Te deben",
                                    size=12,
                                    color=ft.Colors.GREY,
                                ),
                                ft.Text(saldo_text, size=12),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if debt.settled else ft.Icons.PENDING,
                            color=ft.Colors.GREEN if debt.settled else ft.Colors.ORANGE,
                        ),
                    ],
                    spacing=10,
                ),
            )
        )

    def _on_add(e):
        if not dropdown_people.value:
            dropdown_people.error_text = "Selecciona una persona"
            page.update()
            return
        dropdown_people.error_text = None
 
        debt_id = controller.on_save_complete(
            txt_amount.value,
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

    def _on_filter_change(e):
        _refresh()

    dropdown_filter.on_text_change = _on_filter_change
    _refresh()

    return ft.View(
        route="/debts",
        controls=[
            appbar_app(page, "Deudas", user_name),
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [dropdown_people, dropdown_direction, txt_amount],
                            wrap=True,
                            spacing=10,
                        ),
                        ft.Row([txt_desc, txt_max_date], wrap=True, spacing=10),
                        ft.FilledButton(
                            "Agregar deuda", icon=ft.Icons.ADD, on_click=_on_add
                        ),
                        ft.Divider(),
                        dropdown_filter,
                        debts_list,
                    ],
                    spacing=15,
                    expand=True,
                ),
            ),
        ],
    )



