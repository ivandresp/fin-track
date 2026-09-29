import flet as ft
from controllers.person.PersonController import PersonController
from models.person.Person import Person
from views.welcome import appbar_app


def people_view(page: ft.Page, controller: PersonController, user_name: str) -> ft.View:
    txt_name = ft.TextField(label="Nombre", width=300)
    txt_phone = ft.TextField(
        label="Telefono", width=300, keyboard_type=ft.KeyboardType.PHONE
    )
    people_list = ft.ListView(expand=True, spacing=8, padding=10)

    def _refresh():
        people_list.controls.clear()
        for person in controller.on_get_all():
            people_list.controls.append(_row_person(person))
        page.update()

    def _row_person(person: Person) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.PERSON),
                        ft.Column(
                            [
                                ft.Text(person.name, weight=ft.FontWeight.BOLD),
                                ft.Text(person.phone, size=12, color=ft.Colors.GREY),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=10,
                ),
            )
        )

    def _on_add(e):
        person_id = controller.on_save(txt_name.value, txt_phone.value)
        if person_id is not None:
            txt_name.value = ""
            txt_phone.value = ""
            _refresh()
        else:
            page.update()

    _refresh()

    return ft.View(
        route="/people",
        controls=[
            appbar_app("Personas", user_name),
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        ft.Row([txt_name, txt_phone], wrap=True, spacing=10),
                        ft.FilledButton(
                            "Agregar persona", icon=ft.Icons.ADD, on_click=_on_add
                        ),
                        ft.Divider(),
                        people_list,
                    ],
                    spacing=15,
                    expand=True,
                ),
            ),
        ],
    )
