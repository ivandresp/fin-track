import flet as ft

from controllers.person.PersonController import PersonController
from models.person.Person import Person
from views.ui import (
    empty_state,
    grid,
    hero_card,
    initial_avatar,
    page_view,
    panel,
    primary_button,
    section_title,
    text_field,
    tile,
)
from views.welcome import appbar_app


def people_view(page: ft.Page, controller: PersonController, user_name: str) -> ft.View:
    txt_name = text_field("Nombre", col={"xs": 12, "sm": 6})
    txt_phone = text_field(
        "Teléfono", keyboard_type=ft.KeyboardType.PHONE, col={"xs": 12, "sm": 6}
    )

    hero_slot = ft.Container()
    people_area = ft.Column(spacing=12)

    def _row_person(person: Person) -> ft.Container:
        return tile(
            title=person.name,
            subtitle=person.phone or "Sin teléfono",
            leading=initial_avatar(person.name),
        )

    def _render():
        people = controller.on_get_all()
        hero_slot.content = hero_card("Contactos registrados", str(len(people)))
        if people:
            people_area.controls = [grid([_row_person(p) for p in people])]
        else:
            people_area.controls = [
                empty_state(
                    ft.Icons.PEOPLE_OUTLINE,
                    "Aún no tienes contactos",
                    "Agrega a la persona con la que tienes una deuda para empezar.",
                )
            ]

    def _refresh():
        _render()
        page.update()

    def _on_add(e):
        person_id = controller.on_save(txt_name.value, txt_phone.value)
        if person_id is not None:
            txt_name.value = ""
            txt_phone.value = ""
            _refresh()
        else:
            page.update()

    _render()

    form = panel(
        ft.Column(
            [
                section_title("Nueva persona"),
                ft.ResponsiveRow([txt_name, txt_phone], spacing=12, run_spacing=12),
                ft.ResponsiveRow(
                    [primary_button("Guardar persona", _on_add, ft.Icons.PERSON_ADD)]
                ),
            ],
            spacing=14,
        )
    )

    return page_view(
        "/people",
        appbar_app(page, "Personas", user_name),
        hero_slot,
        form,
        section_title("Tus contactos"),
        people_area,
    )