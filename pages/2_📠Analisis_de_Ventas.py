import streamlit as st
from utils.api_client import get_stores, get_products
from components.store_filter import store_filter
from components.product_filter import product_filter

sidebar = st.sidebar
    
# Sidebar para filtros
sidebar.header(" Filtros ")
stores_selected = store_filter(sidebar) 
products_selected = product_filter(sidebar)



aplicar_filtros = sidebar.button("Aplicar Filtros")

if aplicar_filtros:
    st.write("Filtros aplicados")
    st.write(stores_selected)
    st.write(products_selected)
else:
    st.write("Esperando filtros...")
    st.write("Esperando filtros...")