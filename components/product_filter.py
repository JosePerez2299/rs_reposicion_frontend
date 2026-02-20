import pandas as pd
import streamlit as st
from api.products import get_products

def product_filter(box, category_ids=None):
    # Inicializar session state
    if "product_selection_ids" not in st.session_state:
        st.session_state.product_selection_ids = []
    
    if "cached_products" not in st.session_state:
        placeholder = box.empty()
        placeholder.info("Cargando productos...")
        products = get_products()
        st.session_state.cached_products = products
        placeholder.empty()
    
    df = pd.DataFrame(st.session_state.cached_products)

    # Filtrar por categorías si existen
    if category_ids:
        df = df[df["dim_category_id"].isin(category_ids)]
    
    options = df.to_dict(orient="records")
    
    # Preseleccionar productos que están en las opciones filtradas Y en la selección previa
    preselected = [
        prod for prod in options
        if prod["name"] in st.session_state.product_selection_ids
    ]
    
    # Mostrar mensaje mientras se construye el multiselect
    with box:
        with st.spinner("Preparando lista de productos..."):
            selected = st.multiselect(
                "Productos",
                options=options,
                default=preselected,
                format_func=lambda x: x["name"].strip(),
                key="product_multiselect"
            )
    
    # Actualizar la lista de IDs seleccionados
    st.session_state.product_selection_ids = [item["name"].strip() for item in selected]
    
    return st.session_state.product_selection_ids