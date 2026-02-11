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

# Validación ANTES del botón
validacion_ok = True
if not products_selected:
    sidebar.error("⚠️ Debes seleccionar al menos un producto")
    validacion_ok = False

# El botón solo funciona si la validación está ok
aplicar_filtros = sidebar.button("Aplicar Filtros", disabled=not validacion_ok)

if aplicar_filtros:
    st.title("Filtros aplicados")

    body = {
        "dates": dates_selected,
        "stores": stores_selected,
        "products": products_selected,
        "categories": category_selected
    }
    st.write(body)
else:
    st.write("Esperando filtros...")