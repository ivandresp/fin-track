import os
from datetime import date, datetime, timezone, tzinfo
from zoneinfo import ZoneInfo


def _target_timezone() -> tzinfo | None:
    """Zona horaria local. Se puede forzar con la variable FINTRACK_TZ.

    Ejemplo: FINTRACK_TZ=America/Bogota
    Si no está definida, se usa la zona horaria del sistema.
    """
    tz_name = os.getenv("FINTRACK_TZ")
    if not tz_name:
        return None

    try:
        return ZoneInfo(tz_name)
    except Exception:
        return None


def local_today_iso() -> str:
    """Fecha de calendario local en formato ISO (YYYY-MM-DD)."""
    tz = _target_timezone()
    if tz is not None:
        return datetime.now(tz).date().isoformat()
    return date.today().isoformat()


def to_local_datetime(value: datetime | str | None) -> datetime | None:
    """Convierte un timestamp UTC (naive o ISO) a la zona horaria local."""
    if value is None:
        return None

    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    tz = _target_timezone()
    if tz is not None:
        return value.astimezone(tz)
    return value.astimezone()


def format_local_datetime(
    value: datetime | str | None, fmt: str = "%Y-%m-%d %H:%M"
) -> str:
    """Formatea un timestamp UTC en hora local. Devuelve 'Sin fecha' si es None."""
    local_value = to_local_datetime(value)
    if local_value is None:
        return "Sin fecha"
    return local_value.strftime(fmt)
