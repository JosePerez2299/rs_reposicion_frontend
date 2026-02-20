import streamlit as st
import pandas as pd
import api.sales as api_sales


def render(filters): 
    dates = filters['dates']
    stores = filters['stores']
    products = filters['products'] 

    st.header("Análisis Detallado por Producto")
    st.divider()
    if not products:
        st.write("No hay productos seleccionados")
        return

    for index, product in enumerate(products):
        with st.expander(f"#{index + 1} - {product}", expanded= True if index == 0 else False):
            st.write(f"Periodo: {dates['fecha_inicio']} a {dates['fecha_fin']}")
            st.write(f"Tiendas: {stores}")
            st.write(f"Producto: {product}")

            sales_detail = api_sales.get_detail_by_product(product, stores, dates)
            st.write(sales_detail)