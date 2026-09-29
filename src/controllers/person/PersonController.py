import flet as ft
from services.person.PersonService import PersonService


class PersonController:
    def __init__(self, service: PersonService, page: ft.Page):
        self.service = service
        self.page = page

    def on_save(self, name: str, phone: str):
        try:
            person_id = self.service.save(name, phone)
            self._show_msg("Persona guardada correctamente.")
            return person_id
        except ValueError as e:
            self._show_msg(str(e), is_error=True)
            return None

    def on_get_all(self):
        try:
            return self.service.find_all()
        except Exception:
            self._show_msg("No se pudo cargar la lista de personas.", is_error=True)
            return []

    def _show_msg(self, text: str, is_error: bool = False):
        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(text), bgcolor=ft.Colors.RED if is_error else None
            )
        )
