import time
import streamlit as st
from utils.api_client import get_products

DEBOUNCE_MS = 500
MIN_CHARS = 3

def product_filter(box):
    box.subheader("Productos")

    # Inicializar estados
    if "last_input_time" not in st.session_state:
        st.session_state.last_input_time = 0
    
    if "product_options" not in st.session_state:
        st.session_state.product_options = []
    
    if "product_selections" not in st.session_state:
        st.session_state.product_selections = []

    query = box.text_input(
        "Busca por nombre o ID:",
        key="product_search"
    )

    # Solo buscar si cumple requisitos mínimos
    if query and len(query) >= MIN_CHARS:
        now = time.time() * 1000

        if now - st.session_state.last_input_time > DEBOUNCE_MS:
            st.session_state.last_input_time = now
            nuevas_opciones = get_products(search=query)
            
            if nuevas_opciones:
                st.session_state.product_options = nuevas_opciones

    # Mostrar multiselect solo si hay opciones disponibles
    if st.session_state.product_options:
        seleccionados = box.multiselect(
            "Resultados:",
            options=st.session_state.product_options,
            default=st.session_state.product_selections,
            format_func=lambda x: f"{x['name']}",
            key="product_multiselect"
        )
        
        # Actualizar selecciones
        st.session_state.product_selections = seleccionados

        if seleccionados:
            return [item["product_id"] for item in seleccionados]

    return []