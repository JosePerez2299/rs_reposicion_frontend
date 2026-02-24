import streamlit as st
import datetime
import numpy as np
import pandas as pd
import plotly.express as px
from api.sales import get_sales_summary, get_top_sales_products


def render(filtros):
    dates_selected = filtros["dates"]
    stores_selected = filtros["stores"]
    products_selected = filtros["products"]

    st.header("Resumen General")

    # region ============= FILTROS ACTIVOS =============
    with st.expander("🔍 Filtros aplicados", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = datetime.datetime.strptime(
                dates_selected["fecha_inicio"], "%Y-%m-%d"
            )
            fecha_fin = datetime.datetime.strptime(
                dates_selected["fecha_fin"], "%Y-%m-%d"
            )
            st.write(
                f"**📅 Periodo:** {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}"
            )
            st.write(
                f"**🏪 Tiendas:** {'Todas' if len(stores_selected) == 0 else len(stores_selected)} seleccionadas"
            )
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
        metric4.metric("Productos", str(len(filtros["products"])))
    with col5:
        metric5 = st.empty()
        metric5.metric(
            "Tiendas",
            str("Todas" if len(filtros["stores"]) == 0 else len(filtros["stores"])),
        )

    with st.spinner("Cargando datos de ventas..."):
        sales_data = get_sales_summary(filtros)

    if not sales_data:
        st.error("No se pudieron cargar los datos de ventas")
        return

    metric1.metric("Ventas Totales", f"${sales_data['sales']:,.0f}")
    metric2.metric("Transacciones", f"{sales_data['transactions']:,}")
    metric3.metric("Ticket Promedio", f"${sales_data['ticket_promedio']:,.2f}")

    st.divider()
    # endregion

    # region ============= RANKING DE PRODUCTOS =============
    st.subheader("🏆 Ranking de Productos")

    with st.spinner("Cargando ranking de productos..."):
        top_products = get_top_sales_products(products_selected, dates_selected)

    if not top_products:
        st.warning("No hay datos de productos para mostrar")
    else:
        df_productos = pd.DataFrame(top_products)

        # Columnas para mostrar (ocultamos cost)
        display_df = df_productos[
            ["product_name", "qty_sold", "price", "transactions"]
        ].copy()
        display_df.columns = ["Producto", "Unidades", "Monto", "Transacciones"]

        col1, col2 = st.columns([3, 2])

        with col1:
            st.dataframe(
                display_df.style.format(
                    {
                        "Unidades": "{:,.0f}",
                        "Monto": "${:,.2f}",
                        "Transacciones": "{:,}",
                    }
                ).background_gradient(subset=["Unidades"], cmap="YlGn"),
                use_container_width=True,
                hide_index=True,
                height=400,
            )

        with col2:
            st.write("**Distribución de Ventas**")
            fig_pie = px.pie(
                df_productos,
                values="qty_sold",
                names="product_name",
                hole=0.4,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()
    # endregion
