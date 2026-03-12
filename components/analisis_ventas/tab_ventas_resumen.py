import streamlit as st
import datetime
import numpy as np
import pandas as pd
import plotly.express as px
from api.sales import get_sales_summary, get_top_sales_products


def render(filtros):
    dates_selected = filtros["dates"]
    stores_selected = filtros["store_ids"]
    products_selected = filtros["product_codes"]
    all_products = filtros["all_products"]

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
            st.write(f"**📦 Productos:** {len(products_selected) if products_selected else 'Todos'} seleccionados")

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
        metric4.metric("Productos", str(len(products_selected) if products_selected else "Todos"))
    with col5:
        metric5 = st.empty()
        metric5.metric(
            "Tiendas",
            str("Todas" if len(stores_selected) == 0 else len(stores_selected)),
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
    #endregion

    #region ============= RANKING DE PRODUCTOS =============
    st.subheader("🏆 Ranking de Productos")

    with st.spinner("Cargando ranking de productos..."):
        if all_products:
            top_products = []
        else:
            top_products = get_top_sales_products(
                products_selected, stores_selected, dates_selected
            )

    if not top_products:
        st.warning("No hay datos de productos para mostrar")
    else:
        df_productos = pd.DataFrame(top_products)

        # Columnas para mostrar (ocultamos cost)
        display_df = df_productos[
            ["product_name", "qty_sold", "price", "transactions"]
        ].copy()
        display_df.columns = ["Producto", "Unidades", "Monto", "Transacciones"]

        # Agregar columna de posición
        display_df.insert(0, "Posición", range(1, len(display_df) + 1))

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
                width='stretch',
                hide_index=True,
                height=400,
            )

        with col2:
            st.write("**Distribución de Ventas**")
            
            MAX_SLICE = 10
            
            if len(df_productos) > MAX_SLICE:
                top_df = df_productos.nlargest(MAX_SLICE, "qty_sold").copy()
                otros_qty = df_productos.nsmallest(len(df_productos) - MAX_SLICE, "qty_sold")["qty_sold"].sum()
                otros_row = pd.DataFrame([{"product_name": f"Otros ({len(df_productos) - MAX_SLICE})", "qty_sold": otros_qty}])
                chart_df = pd.concat([top_df, otros_row], ignore_index=True)
            else:
                chart_df = df_productos.copy()

            fig_pie = px.pie(
                chart_df,
                values="qty_sold",
                names="product_name",
                hole=0.4,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_pie, width="stretch")

    st.divider()
    #endregion
