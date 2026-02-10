from datetime import datetime, date, timedelta
import streamlit as st


def dates_filter(box):
    box.subheader("Rango de Fechas")

    hoy = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1)
    hace_90_dias = hoy - timedelta(days=90)

    fechas = box.date_input(
        "Selecciona el intervalo (desde - hasta):",
        value=(inicio_mes, hoy),
        min_value=hace_90_dias,
        max_value=hoy,
        format="DD/MM/YYYY",
        help="Selecciona un rango de fechas (máximo 90 días) o un solo día"
    )

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