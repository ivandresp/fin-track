import flet as ft

from views.ui import (
    ACCENT,
    BG,
    PRIMARY,
    SURFACE_2,
    TEXT,
    TEXT_MUTED,
    WHITE,
    gradient,
    primary_button,
    text_field,
    tint,
)

USER_NAME_KEY = "user_name"


async def get_user_name(page: ft.Page) -> str | None:
    return await ft.SharedPreferences().get(USER_NAME_KEY)


async def save_user_name(page: ft.Page, name: str):
    await ft.SharedPreferences().set(USER_NAME_KEY, name)


def welcome_view(page: ft.Page, on_continue) -> ft.View:
    txt_name = text_field("¿Cómo te llamas?", autofocus=True, col=12)

    async def _on_continue(e):
        name = (txt_name.value or "").strip()
        if not name:
            txt_name.error = "Escribe tu nombre para continuar"
            page.update()
            return
        txt_name.error = None
        await save_user_name(page, name)
        await on_continue(name)

    txt_name.on_submit = _on_continue

    logo = ft.Container(
        width=88,
        height=88,
        border_radius=28,
        gradient=gradient(),
        alignment=ft.Alignment(0, 0),
        shadow=ft.BoxShadow(
            blur_radius=30, color=tint(PRIMARY, 0.4), offset=ft.Offset(0, 12)
        ),
        content=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=42, color=WHITE),
    )

    card = ft.Container(
        col={"xs": 12, "sm": 9, "md": 7, "lg": 5, "xl": 4},
        padding=ft.Padding(left=24, top=24, right=24, bottom=24),
        content=ft.Column(
            [
                ft.Row([logo], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text(
                    "Bienvenido a FinTrack",
                    size=26,
                    weight=ft.FontWeight.W_700,
                    color=TEXT,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Registra tus ingresos, gastos y deudas en un solo lugar.",
                    size=14,
                    color=TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=4),
                txt_name,
                primary_button("Comenzar", _on_continue, ft.Icons.ARROW_FORWARD),
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )

    return ft.View(
        route="/welcome",
        bgcolor=BG,
        padding=0,
        controls=[
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.ResponsiveRow([card], alignment=ft.MainAxisAlignment.CENTER)
                ],
            )
        ],
    )


def appbar_app(
    page: ft.Page, title: str, user_name: str, show_back: bool = True
) -> ft.AppBar:
    short_name = user_name if len(user_name) <= 14 else user_name[:13] + "…"

    user_chip = ft.Container(
        padding=ft.Padding(left=12, top=6, right=10, bottom=6),
        border_radius=20,
        bgcolor=SURFACE_2,
        content=ft.Row(
            [
                ft.Text(short_name, size=13, color=TEXT),
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=20, color=ACCENT),
            ],
            spacing=6,
            tight=True,
        ),
    )

    return ft.AppBar(
        leading=(
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=TEXT,
                tooltip="Volver al inicio",
                on_click=lambda e: page.navigate("/"),
            )
            if show_back
            else None
        ),
        title=ft.Text(title, size=18, weight=ft.FontWeight.W_600, color=TEXT),
        center_title=False,
        bgcolor=BG,
        actions=[user_chip, ft.Container(width=12)],
    )