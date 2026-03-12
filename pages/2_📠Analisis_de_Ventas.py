import datetime
import streamlit as st
from components.analisis_ventas import sidebar_filters, tab_datos_crudos, tab_ventas_resumen
from components.analisis_ventas import *

# ============= CONFIGURACIÓN DE PÁGINA =============
st.set_page_config(
    page_title="Dashboard de Ventas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============= SIDEBAR CON filters =============
sidebar = st.sidebar
sidebar.header("Filtros")

sidebar_filters.render()
filters = st.session_state.get("analisis_ventas_filters", {})

# ============= NAVEGACIÓN ====================
st.title("📊 Dashboard de Ventas e Inventario")

# ============= LÓGICA DE filters =============
if filters:

    # Crear tabs SOLO cuando hay filters aplicados Y NO hay cambios pendientes
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📈 Resumen General",
            "🔍 Análisis Detallado",
            "📊 Comparativas",
            "📦 Inventario y Rotación",
            "💾 Datos Crudos",
        ]
    )

    # ============= TAB 1: RESUMEN GENERAL =============
    with tab1:
        with st.spinner("⏳ Cargando resumen general..."):
            if filters["product_codes"] or filters["all_products"]:
                tab_ventas_resumen.render(filters)
            else:
                st.write("⚠️ No hay filters aplicados")

    # ============= TAB 2: ANÁLISIS DETALLADO =============
    with tab2:
        with st.spinner("⏳ Cargando análisis detallado..."):
            st.write("⚠️ Desarrollo en curso...")
            #tab_ventas_analisis_detallado.render(filters)

    with tab3:
        with st.spinner("⏳ Cargando comparativas..."):
            st.write("⚠️ Desarrollo en curso...")
            #tab_comparativas.render(filters)

    with tab4: 
        with st.spinner("⏳ Cargando inventario y rotación..."):
            st.write("⚠️ Inventario y rotación")
    with tab5:
        with st.spinner("⏳ Cargando datos crudos..."):
            tab_datos_crudos.render(filters)
else:
    st.divider()
    st.info(
        "👈 Selecciona los filters en el panel lateral y presiona 'Aplicar filters' para comenzar"
    )
