from datetime import datetime
from zoneinfo import ZoneInfo

# Huso horario argentino vía la base de datos IANA (zoneinfo + tzdata), no un
# offset fijo hardcodeado: si Argentina cambiara sus reglas de horario en el
# futuro, esto se actualiza solo con la librería, sin tocar código.
TZ_ARGENTINA = ZoneInfo("America/Argentina/Buenos_Aires")


def now_ar() -> datetime:
    """Hora actual en huso horario argentino, con tzinfo adjunto."""
    return datetime.now(TZ_ARGENTINA)


def localize_ar(dt: datetime | None) -> datetime | None:
    """Adjunta el tzinfo argentino a un datetime naive leído de la base
    (columna TIMESTAMP sin huso horario) para que se serialice con el
    offset correcto (-03:00) hacia el frontend. No convierte el valor,
    solo lo etiqueta: asume que lo guardado ya son horas argentinas
    (ver now_ar())."""
    if dt is None:
        return None
    return dt.replace(tzinfo=TZ_ARGENTINA)
