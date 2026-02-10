import streamlit as st
from components.store_filter import store_filter
from components.product_filter import product_filter
from components.dates_filters import dates_filter
from components.category_filter import category_filter

sidebar = st.sidebar
    
# Sidebar para filtros
sidebar.header(" Filtros ")
dates_selected = dates_filter(sidebar)
stores_selected = store_filter(sidebar) 
category_selected = category_filter(sidebar)
products_selected = product_filter(sidebar, category_ids=category_selected)



aplicar_filtros = sidebar.button("Aplicar Filtros")

if aplicar_filtros:
    st.title("Filtros aplicados")
    st.write("Fechas")
    st.write(dates_selected)
    st.write("Tiendas")
    st.write(stores_selected)
    st.write("Productos")
    st.write(products_selected)
    st.write("Categorías")
    st.write(category_selected)
else:
    st.write("Esperando filtros...")