from datetime import datetime, date
import streamlit as st


def dates_filter(box):
    box.subheader("Rango de Fechas")

    hoy = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1)

    fechas = box.date_input(
        "Selecciona el intervalo:",
        value=(inicio_mes, hoy),
        min_value=date(2000, 1, 1),
        max_value=hoy,
        format="DD/MM/YYYY"
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