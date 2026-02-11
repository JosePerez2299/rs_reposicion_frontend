import streamlit as st
import datetime

from utils.api_client import get_total_sales_data


def render(filtros):
    dates_selected = filtros['dates']
    stores_selected = filtros['stores']
    products_selected = filtros['products']
    
    st.header("Resumen General")

    # ============= FILTROS ACTIVOS =============
    with st.expander("🔍 Filtros aplicados", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = datetime.datetime.strptime(dates_selected['fecha_inicio'], "%Y-%m-%d")
            fecha_fin = datetime.datetime.strptime(dates_selected['fecha_fin'], "%Y-%m-%d")
            st.write(f"**📅 Periodo:** {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}")
            st.write(f"**🏪 Tiendas:** {len(stores_selected)} seleccionadas")
        with col2:
            st.write(f"**📦 Productos:** {len(products_selected)} seleccionados")
    
    st.divider()

    
    # ============= MÉTRICAS PRINCIPALES =============
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        metric1 = st.empty()
        metric1.metric("Ventas Totales", "$0")
    with col2:
        metric2 = st.empty()
        metric2.metric("Transacciones", "0")
    with col3:
        metric3 = st.empty()
        metric3.metric("Ticket Promedio", "$0.00")
    with col4:
        metric4 = st.empty()
        metric4.metric("Productos", str(len(filtros['products'])))
    with col5:
        metric5 = st.empty()
        metric5.metric("Tiendas", str(len(filtros['stores'])))
    
    with st.spinner("Cargando datos de ventas..."):
        sales_data = get_total_sales_data()
    
    if not sales_data:
        st.error("No se pudieron cargar los datos de ventas")
        return
    
    metric1.metric("Ventas Totales", f"${sales_data['sales']:,.0f}")
    metric2.metric("Transacciones", f"{sales_data['transactions']:,}")
    metric3.metric("Ticket Promedio", f"${sales_data['ticket_promedio']:,.2f}")

    st.divider()