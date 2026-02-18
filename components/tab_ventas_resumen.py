import streamlit as st
import datetime
import numpy as np
import pandas as pd
import plotly.express as px

from utils.api_client import get_total_sales_data


def render(filtros):
    dates_selected = filtros['dates']
    stores_selected = filtros['stores']
    products_selected = filtros['products']
    
    st.header("Resumen General")

    # region ============= FILTROS ACTIVOS =============
    with st.expander("🔍 Filtros aplicados", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = datetime.datetime.strptime(dates_selected['fecha_inicio'], "%Y-%m-%d")
            fecha_fin = datetime.datetime.strptime(dates_selected['fecha_fin'], "%Y-%m-%d")
            st.write(f"**📅 Periodo:** {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}")
            st.write(f"**🏪 Tiendas:** {'Todas' if len(stores_selected) == 0 else len(stores_selected)} seleccionadas")
        with col2:
            st.write(f"**📦 Productos:** {len(products_selected)} seleccionados")
    
    st.divider()
    # endregion
    
    # region ============= TO DO: MÉTRICAS PRINCIPALES =============
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
        metric5.metric("Tiendas", str('Todas' if len(filtros['stores']) == 0 else len(filtros['stores'])))
    
    with st.spinner("Cargando datos de ventas..."):
        sales_data = get_total_sales_data()
    
    if not sales_data:
        st.error("No se pudieron cargar los datos de ventas")
        return
    
    metric1.metric("Ventas Totales", f"${sales_data['sales']:,.0f}")
    metric2.metric("Transacciones", f"{sales_data['transactions']:,}")
    metric3.metric("Ticket Promedio", f"${sales_data['ticket_promedio']:,.2f}")

    st.divider()
    # endregion
    
       
    # region ============= TO DO: RANKING DE PRODUCTOS =============
    st.subheader("🏆 Ranking de Productos")
    
    # Data dummy
    productos = ['Producto ' + str(i) for i in range(1, 11)]
    ventas = [np.random.randint(1000, 100000) for _ in range(10)]
    transacciones = [np.random.randint(100, 1000) for _ in range(10)]
    
    df_productos = pd.DataFrame({
        "producto": productos,
        "ventas": ventas,
        "transacciones": transacciones
    })
    
    df_productos['ticket_promedio'] = (df_productos['ventas'] / df_productos['transacciones']).round(2)
    df_productos['porcentaje'] = (df_productos['ventas'] / sales_data['sales'] * 100).round(1)
    df_productos = df_productos.sort_values("ventas", ascending=False)
    df_productos['ranking'] = range(1, len(df_productos) + 1)
    df_productos = df_productos[['ranking', 'producto', 'ventas', 'transacciones', 'ticket_promedio', 'porcentaje']]
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.dataframe(
            df_productos.style.format({
                "ventas": "${:,.0f}",
                "transacciones": "{:,}",
                "ticket_promedio": "${:,.2f}",
                "porcentaje": "{:.1f}%"
            }).background_gradient(subset=['ventas'], cmap='YlGn'),
            width='stretch',
            hide_index=True,
            height=400
        )
    
    with col2:
        st.write("**Distribución de Ventas**")
        fig_pie = px.pie(
            df_productos, 
            values='ventas', 
            names='producto',
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_pie, width='stretch')
    
    st.divider()
    # endregion
    