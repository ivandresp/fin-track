import flet as ft

from views.ui import (
    ACCENT,
    SUCCESS,
    SURFACE,
    TEXT,
    TEXT_MUTED,
    WARNING,
    hero_card,
    icon_box,
    page_view,
    section_title,
)
from views.welcome import appbar_app

# ruta, título, descripción, icono, color
SHORTCUTS = [
    ("/transactions", "Transacciones", "Ingresos y gastos", ft.Icons.SWAP_VERT, ACCENT),
    ("/debts", "Deudas", "Lo que debes y te deben", ft.Icons.MONEY_OFF, WARNING),
    ("/payments", "Pagos", "Abonos a tus deudas", ft.Icons.PAYMENTS, SUCCESS),
    ("/people", "Personas", "Tus contactos", ft.Icons.PEOPLE, "#7DB8FF"),
]


def home_view(page: ft.Page, user_name: str) -> ft.View:
    def _shortcut(route: str, title: str, hint: str, icon: str, color: str):
        return ft.Container(
            # 2 por fila en móvil, 4 en una sola fila desde tablet
            col={"xs": 6, "md": 3},
            padding=18,
            bgcolor=SURFACE,
            border_radius=22,
            ink=True,
            on_click=lambda e, r=route: page.navigate(r),
            content=ft.Column(
                [
                    icon_box(icon, color),
                    ft.Container(height=2),
                    ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=TEXT),
                    ft.Text(hint, size=12, color=TEXT_MUTED),
                ],
                spacing=4,
            ),
        )

    return page_view(
        "/",
        appbar_app(page, "FinTrack", user_name, show_back=False),
        hero_card("Bienvenido de nuevo", user_name),
        section_title("¿Qué quieres hacer hoy?"),
        ft.ResponsiveRow(
            [_shortcut(*s) for s in SHORTCUTS], spacing=12, run_spacing=12
        ),
    )