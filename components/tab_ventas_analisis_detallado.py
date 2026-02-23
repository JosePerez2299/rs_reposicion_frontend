import streamlit as st
import pandas as pd
import api.sales as api_sales


def render(filters):
    dates = filters["dates"]
    stores = filters["stores"]
    products = filters["products"]

    st.header("Análisis Detallado por Producto")
    if not products:
        st.write("No hay productos seleccionados")
        return

    for index, product in enumerate(products):
        with st.expander(
            f"#{index + 1} - {product}", expanded=True if index == 0 else False
        ):

            sales_detail = api_sales.get_detail_by_product(product, stores, dates)

            if not sales_detail:
                st.write("No hay datos para mostrar")
                continue

            df = pd.DataFrame(sales_detail)

            # Calcular totales del DataFrame completo
            total_ventas = df["qty_solded"].sum()
            total_transacciones = df["transactions"].sum()
            total_stock = df["stock"].sum()
            total_monto = df["total"].sum()

            # Mostrar resumen
            st.subheader("Resumen")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Unidades Vendidas", f"{total_ventas:,.0f}")
            with col2:
                st.metric("Transacciones", f"{total_transacciones:,.0f}")
            with col3:
                st.metric("Stock Total", f"{total_stock:,.0f}")
            with col4:
                st.metric("Monto Total", f"${total_monto:,.2f}")

            col1, col2 = st.columns(2)
            with col1:
                if "store_name" in df.columns:
                    selected_stores = st.multiselect(
                        "Selecciona las tiendas",
                        df["store_name"].unique(),
                        key=f"stores_{index}",
                    )
                else:
                    selected_stores = []
            with col2:
                if "product_id" in df.columns:
                    products_ids = st.multiselect(
                        "Selecciona las variantes",
                        sorted(df["product_id"].unique()),
                        format_func=lambda x: f"{x[-3:]}",
                        key=f"products_{index}",
                    )
                else:
                    products_ids = []

            if selected_stores and "store_name" in df.columns:
                filtered_df = df[df["store_name"].isin(selected_stores)]
            else:
                filtered_df = df

            if products_ids and "product_id" in df.columns:
                filtered_df = filtered_df[filtered_df["product_id"].isin(products_ids)]

            # Ocultar columna product_name del DataFrame
            if "product_name" in filtered_df.columns:
                filtered_df = filtered_df.drop("product_name", axis=1)

            st.dataframe(filtered_df, width="stretch")
