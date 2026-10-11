"""
views/ui.py

Sistema de diseño compartido por todas las vistas.

Dirección visual (tomada de la imagen de referencia): fondo oscuro con tinte
violeta, paneles redondeados, una sola tarjeta protagonista con degradado por
pantalla y botones tipo píldora. El degradado se reserva para esa tarjeta y
para el botón principal; todo lo demás es plano y silencioso.

Responsive: todo el contenido vive dentro de un ResponsiveRow, así que se
adapta solo a móvil, tablet y escritorio sin escuchar eventos de resize.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Callable

import flet as ft

# ── Paleta ───────────────────────────────────────────────────────────────
BG = "#120F1A"          # fondo de la app
SURFACE = "#1C1827"     # paneles y tarjetas
SURFACE_2 = "#272134"   # campos, chips, cajas de iconos
PRIMARY = "#8B2FE3"     # violeta principal
PRIMARY_DEEP = "#4C1D95"
ACCENT = "#C4A1FF"      # violeta claro para iconos y foco
TEXT = "#F5F2FB"
TEXT_MUTED = "#9D94B1"
DANGER = "#FF5470"
SUCCESS = "#3DDC97"
WARNING = "#FFB547"
WHITE = "#FFFFFF"

# ── Columnas responsive (sistema de 12 columnas) ─────────────────────────
# Ancho del contenido: completo en móvil/tablet, centrado y acotado en escritorio.
CONTENT_COL = {"xs": 12, "lg": 10, "xl": 8, "xxl": 6}
# Tarjetas de lista: 1 columna en móvil, 2 desde tablet.
GRID_COL = {"xs": 12, "sm": 6}
# Campos de formulario: 1 columna en móvil, 2 en tablet, 3 en escritorio.
FIELD_COL = {"xs": 12, "sm": 6, "md": 4}


def tint(color: str, opacity: float) -> str:
    return ft.Colors.with_opacity(opacity, color)


def gradient() -> ft.LinearGradient:
    return ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=[PRIMARY, PRIMARY_DEEP],
    )


def money(value) -> str:
    """Decimal -> '$1,234.50' (con signo menos delante si es negativo)."""
    value = Decimal(value)
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def apply_theme(page: ft.Page) -> None:
    """Llamar una vez al inicio de main(page)."""
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0
    page.theme = ft.Theme(color_scheme_seed=PRIMARY)
    page.dark_theme = ft.Theme(color_scheme_seed=PRIMARY)


# ── Estructura de página ─────────────────────────────────────────────────
def page_view(route: str, appbar: ft.AppBar, *sections: ft.Control) -> ft.View:
    """Vista con scroll vertical y contenido centrado/acotado según el ancho."""
    content = ft.Container(
        col=CONTENT_COL,
        padding=ft.Padding(left=16, top=8, right=16, bottom=40),
        content=ft.Column(list(sections), spacing=18),
    )
    return ft.View(
        route=route,
        bgcolor=BG,
        padding=0,
        controls=[
            appbar,
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.ResponsiveRow([content], alignment=ft.MainAxisAlignment.CENTER)
                ],
            ),
        ],
    )


def section_title(text: str) -> ft.Text:
    return ft.Text(text, size=17, weight=ft.FontWeight.W_600, color=TEXT)


def panel(content: ft.Control) -> ft.Container:
    return ft.Container(
        content=content, padding=18, bgcolor=SURFACE, border_radius=22
    )


# ── Tarjeta protagonista ─────────────────────────────────────────────────
def _hero_stat(label: str, value: str, icon: str) -> ft.Container:
    return ft.Container(
        expand=True,
        padding=ft.Padding(left=12, top=10, right=12, bottom=10),
        border_radius=16,
        bgcolor=tint(WHITE, 0.16),
        content=ft.Row(
            [
                ft.Icon(icon, size=18, color=WHITE),
                ft.Column(
                    [
                        ft.Text(label, size=11, color=tint(WHITE, 0.75)),
                        ft.Text(
                            value,
                            size=14,
                            weight=ft.FontWeight.W_600,
                            color=WHITE,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ],
            spacing=8,
        ),
    )


def hero_card(
    label: str,
    amount: str,
    stats: list[tuple[str, str, str]] | None = None,
) -> ft.Container:
    """Etiqueta pequeña + cifra grande, con chips opcionales (etiqueta, valor, icono)."""
    items: list[ft.Control] = [
        ft.Text(label, size=13, color=tint(WHITE, 0.75)),
        ft.Text(
            amount,
            size=32,
            weight=ft.FontWeight.W_700,
            color=WHITE,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        ),
    ]
    if stats:
        items.append(ft.Container(height=8))
        items.append(ft.Row([_hero_stat(*s) for s in stats], spacing=10))

    return ft.Container(
        content=ft.Column(items, spacing=4),
        padding=22,
        border_radius=28,
        gradient=gradient(),
        shadow=ft.BoxShadow(
            blur_radius=30,
            color=tint(PRIMARY, 0.35),
            offset=ft.Offset(0, 12),
        ),
    )


# ── Campos y botones ─────────────────────────────────────────────────────
def text_field(label: str, **kwargs) -> ft.TextField:
    kwargs.setdefault("col", FIELD_COL)
    return ft.TextField(
        label=label,
        filled=True,
        fill_color=SURFACE_2,
        border_radius=14,
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT,
        text_size=14,
        **kwargs,
    )


def dropdown(label: str, options: list, value: str | None = None, **kwargs) -> ft.Dropdown:
    kwargs.setdefault("col", FIELD_COL)
    return ft.Dropdown(
        label=label,
        options=options,
        value=value,
        filled=True,
        fill_color=SURFACE_2,
        border_radius=14,
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=ACCENT,
        text_size=14,
        **kwargs,
    )


def primary_button(
    text: str,
    on_click,
    icon: str | None = None,
    col: dict | None = None,
) -> ft.Container:
    """Botón píldora con degradado. En móvil ocupa todo el ancho."""
    content: list[ft.Control] = []
    if icon:
        content.append(ft.Icon(icon, color=WHITE, size=20))
    content.append(
        ft.Text(text, color=WHITE, size=15, weight=ft.FontWeight.W_600)
    )
    return ft.Container(
        content=ft.Row(content, alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        padding=ft.Padding(left=24, top=14, right=24, bottom=14),
        border_radius=28,
        gradient=gradient(),
        ink=True,
        on_click=on_click,
        col=col or {"xs": 12, "sm": 6, "md": 4},
    )


class PillSelector:
    """Selector de filtro tipo píldora (como el Débito/Crédito de la referencia).

    options: [(clave, etiqueta), ...]. on_change recibe la clave elegida.
    En pantallas angostas se desplaza horizontalmente.
    """

    def __init__(
        self,
        options: list[tuple[str, str]],
        value: str,
        on_change: Callable[[str], None],
    ):
        self._options = options
        self._value = value
        self._on_change = on_change
        self.control = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
        self._build()

    @property
    def value(self) -> str:
        return self._value

    def _build(self) -> None:
        self.control.controls = [self._pill(k, label) for k, label in self._options]

    def _pill(self, key: str, label: str) -> ft.Container:
        active = key == self._value
        return ft.Container(
            content=ft.Text(
                label,
                size=13,
                weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_500,
                color=WHITE if active else TEXT_MUTED,
            ),
            padding=ft.Padding(left=16, top=9, right=16, bottom=9),
            border_radius=20,
            bgcolor=PRIMARY if active else SURFACE_2,
            on_click=lambda e, k=key: self._select(k),
        )

    def _select(self, key: str) -> None:
        if key == self._value:
            return
        self._value = key
        self._build()
        self._on_change(key)


# ── Piezas de lista ──────────────────────────────────────────────────────
def icon_box(icon: str, color: str) -> ft.Container:
    return ft.Container(
        width=46,
        height=46,
        border_radius=14,
        bgcolor=tint(color, 0.16),
        alignment=ft.Alignment(0, 0),
        content=ft.Icon(icon, color=color, size=22),
    )


def initial_avatar(name: str) -> ft.Container:
    letter = (name or "?").strip()[:1].upper() or "?"
    return ft.Container(
        width=46,
        height=46,
        border_radius=23,
        gradient=gradient(),
        alignment=ft.Alignment(0, 0),
        content=ft.Text(letter, size=18, weight=ft.FontWeight.W_700, color=WHITE),
    )


def badge(text: str, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=11, weight=ft.FontWeight.W_600, color=color),
        padding=ft.Padding(left=10, top=3, right=10, bottom=3),
        border_radius=10,
        bgcolor=tint(color, 0.15),
    )


def progress_bar(fraction: float, color: str) -> ft.Container:
    """Barra de progreso hecha con dos contenedores flexibles (0.0 a 1.0)."""
    pct = max(0, min(100, round(fraction * 100)))
    parts: list[ft.Control] = []
    if pct > 0:
        parts.append(ft.Container(expand=pct, height=6, bgcolor=color, border_radius=3))
    if pct < 100:
        parts.append(ft.Container(expand=100 - pct, height=6))
    return ft.Container(
        content=ft.Row(parts, spacing=0),
        height=6,
        bgcolor=SURFACE_2,
        border_radius=3,
    )


def tile(
    title: str,
    subtitle: str,
    leading: ft.Control,
    value: str | None = None,
    value_color: str = TEXT,
    aside: ft.Control | str | None = None,
    footer: ft.Control | None = None,
) -> ft.Container:
    """Fila de lista: icono/avatar, dos líneas de texto y un valor a la derecha."""
    right: list[ft.Control] = []
    if value is not None:
        right.append(
            ft.Text(value, size=15, weight=ft.FontWeight.W_700, color=value_color)
        )
    if isinstance(aside, str):
        right.append(ft.Text(aside, size=11, color=TEXT_MUTED))
    elif aside is not None:
        right.append(aside)

    header = ft.Row(
        [
            leading,
            ft.Column(
                [
                    ft.Text(
                        title,
                        size=15,
                        weight=ft.FontWeight.W_600,
                        color=TEXT,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        subtitle,
                        size=12,
                        color=TEXT_MUTED,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=2,
                expand=True,
            ),
            ft.Column(
                right, spacing=4, horizontal_alignment=ft.CrossAxisAlignment.END
            ),
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    body: list[ft.Control] = [header]
    if footer is not None:
        body.append(footer)

    return ft.Container(
        content=ft.Column(body, spacing=12),
        padding=14,
        bgcolor=SURFACE,
        border_radius=18,
    )


def grid(items: list[ft.Control]) -> ft.ResponsiveRow:
    """Distribuye las tarjetas: 1 columna en móvil, 2 desde tablet."""
    for item in items:
        item.col = GRID_COL
    return ft.ResponsiveRow(items, spacing=12, run_spacing=12)


def empty_state(icon: str, title: str, hint: str) -> ft.Container:
    return ft.Container(
        padding=ft.Padding(left=16, top=28, right=16, bottom=28),
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            [
                ft.Icon(icon, size=40, color=ACCENT),
                ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=TEXT),
                ft.Text(
                    hint,
                    size=13,
                    color=TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )