import streamlit as st
from components.store_filter import store_filter
from components.product_filter import product_filter
from components.dates_filters import dates_filter

sidebar = st.sidebar
    
# Sidebar para filtros
sidebar.header(" Filtros ")
dates_selected = dates_filter(sidebar)
stores_selected = store_filter(sidebar) 
products_selected = product_filter(sidebar)



aplicar_filtros = sidebar.button("Aplicar Filtros")

if aplicar_filtros:
    st.write("Filtros aplicados")
    st.write(dates_selected)
    st.write(stores_selected)
    st.write(products_selected)
else:
    st.write("Esperando filtros...")