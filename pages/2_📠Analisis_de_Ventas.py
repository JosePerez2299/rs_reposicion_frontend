import datetime
import streamlit as st
from components.store_filter import store_filter
from components.product_filter import product_filter
from components.dates_filters import dates_filter
from components.category_filter import category_filter
from components import tab_ventas_analisis_detallado, tab_ventas_resumen

# ============= CONFIGURACIÓN DE PÁGINA =============
st.set_page_config(
    page_title="Dashboard de Ventas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============= INICIALIZAR SESSION STATE =============
if "page_2_filtros_aplicados" not in st.session_state:
    st.session_state["page_2_filtros_aplicados"] = False

if "page_2_filtros" not in st.session_state:
    st.session_state["page_2_filtros"] = None

# ============= SIDEBAR CON FILTROS =============
sidebar = st.sidebar
sidebar.header(" Filtros ")

dates_selected = dates_filter(sidebar)
stores_selected = store_filter(sidebar)
category_selected = category_filter(sidebar)
products_selected = product_filter(sidebar, category_ids=category_selected)

# ======== TO DO: REVERTIR ? =====================


# filtros_actuales = {
#     "dates": dates_selected,
#     "stores": stores_selected,
#     "category": category_selected,
#     "products": products_selected,
# }


filtros_actuales = {
    "dates": {"fecha_inicio": "2026-02-01", "fecha_fin": "2026-02-11"},
    "stores": [101,102],
    "category": [],
    "products": [
        "BOLSO EPONA - NAVY/PURPLE",
        "BOLSO EPONA - BLACK/GOLD",
        "BOLSO EPONA - BLACK/WHITE",
        "BOLSO EPONA - BLACK/BLUE",
        "BOLSO EPONA - BLACK/RED",
    ],
}

# Eliminar cuando se revierta el cambio
st.session_state["page_2_filtros_aplicados"] = True
st.session_state["page_2_filtros"] = filtros_actuales
# ======================================= 


# Validación ANTES del botón
validacion_ok = True
if not products_selected:
    sidebar.error("⚠️ Debes seleccionar al menos un producto")
    validacion_ok = False

aplicar_filtros = sidebar.button("Aplicar Filtros", disabled=not validacion_ok)

if aplicar_filtros:
    st.session_state["page_2_filtros_aplicados"] = True
    st.session_state["page_2_filtros"] = filtros_actuales

filtros_cambiaron = (
    st.session_state["page_2_filtros_aplicados"]
    and st.session_state["page_2_filtros"] != filtros_actuales
)

# ============= NAVEGACIÓN ====================
st.title("📊 Dashboard de Ventas e Inventario")
if not st.session_state["page_2_filtros_aplicados"] or filtros_cambiaron:
    st.divider()

# ============= LÓGICA DE FILTROS =============
if st.session_state["page_2_filtros_aplicados"] and not filtros_cambiaron:

    # Crear tabs SOLO cuando hay filtros aplicados Y NO hay cambios pendientes
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
            tab_ventas_resumen.render(st.session_state["page_2_filtros"])

    # ============= TAB 2: ANÁLISIS DETALLADO =============
    with tab2:
        with st.spinner("⏳ Cargando resumen general..."):
            tab_ventas_analisis_detallado.render(st.session_state["page_2_filtros"])

    # ... resto de tabs

elif filtros_cambiaron:
    st.warning(
        "⚠️ Has modificado los filtros. Presiona 'Aplicar Filtros' para actualizar el dashboard."
    )

else:
    st.info(
        "👈 Selecciona los filtros en el panel lateral y presiona 'Aplicar Filtros' para comenzar"
    )
