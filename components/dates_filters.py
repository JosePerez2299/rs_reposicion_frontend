from datetime import datetime, date, timedelta
import streamlit as st


def dates_filter(box):

    hoy = date.today()
    ayer = hoy - timedelta(days=1)
    max_pasado = hoy - timedelta(days=180)    

    fechas = box.date_input(
        "Fecha",
        value=(hoy - timedelta(days=30), ayer),
        min_value=max_pasado,
        max_value=ayer,
        format="DD/MM/YYYY",
        help="Selecciona un rango de fechas (máximo 180 días) o un solo día"
    )

    # Calcular y mostrar el período seleccionado en días
    if isinstance(fechas, tuple) and len(fechas) == 2:
        dias_seleccionados = (fechas[1] - fechas[0]).days + 1
        box.info(f"Período seleccionado: {dias_seleccionados} días")
    elif isinstance(fechas, (date,)) or (isinstance(fechas, tuple) and len(fechas) == 1):
        dias_seleccionados = 1
        box.info(f"Período seleccionado: {dias_seleccionados} día")

    # Manejar tanto un solo día como un rango
    if isinstance(fechas, tuple):
        if len(fechas) == 2:
            # Rango de fechas
            return {
                "fecha_inicio": fechas[0].isoformat(),
                "fecha_fin": fechas[1].isoformat()
            }
        elif len(fechas) == 1:
            # Un solo día (usar el mismo día como inicio y fin)
            return {
                "fecha_inicio": fechas[0].isoformat(),
                "fecha_fin": fechas[0].isoformat()
            }
    elif isinstance(fechas, date):
        # Por si acaso devuelve un solo date object
        return {
            "fecha_inicio": fechas.isoformat(),
            "fecha_fin": fechas.isoformat()
        }

    return None