import flet as ft

USER_NAME_KEY = "user_name"

async def get_user_name(page:ft.Page) -> str | None:
    return await ft.SharedPreferences().get(USER_NAME_KEY)

async def save_user_name(page:ft.Page, name:str):
    await ft.SharedPreferences().set(USER_NAME_KEY, name)

def welcome_view(page:ft.Page, on_continue) -> ft.View:
    txt_name = ft.TextField(label="¿Cómo te llamas?", autofocus=True, width=300)

    async def _on_click(e):
        name = (txt_name.value or "").strip()
        if not name:
            txt_name.error = "Ingresa tu nombre para continuar"
            page.update()
            return
        await save_user_name(page, name)
        await on_continue(name)

    return ft.View(
        route="/welcome",
        controls=[
            ft.Column(
                [
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=64),
                    ft.Text("Bienvenido a FinTrack", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("¿Como quieres que te llamemos?"),
                    txt_name,
                    ft.FilledButton("Continuar", on_click=_on_click),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

def appbar_app(title:str, user_name:str) -> ft.AppBar:
    return ft.AppBar(
        title=ft.Text(title),
        center_title=False,
        actions=[
            ft.Row(
                [ft.Icon(ft.Icons.ACCOUNT_CIRCLE), ft.Text(user_name)],
                spacing=5,
            ),
            ft.Container(width=15),
        ],
    )