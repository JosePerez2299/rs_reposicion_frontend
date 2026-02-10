import time
import streamlit as st
from utils.api_client import get_products

DEBOUNCE_MS = 500
MIN_CHARS = 3

def product_filter(box, category_ids=None):  # Cambio: category_id -> category_ids

    if "last_input_time" not in st.session_state:
        st.session_state.last_input_time = 0
    
    if "product_options" not in st.session_state:
        st.session_state.product_options = []
    
    if "product_selections" not in st.session_state:
        st.session_state.product_selections = []
    
    # Detectar cambio de categorías y limpiar selecciones
    if "last_categories" not in st.session_state:  # Cambio: last_category -> last_categories
        st.session_state.last_categories = None
    
    # Comparar listas en lugar de valores únicos
    if st.session_state.last_categories != category_ids:
        st.session_state.product_options = []
        st.session_state.product_selections = []
        st.session_state.last_categories = category_ids

    query = box.text_input(
        "Encontrar producto",
        key="product_search",
        help="Solo para búsqueda por nombre o ID, se debe seleccionar en el filtro de productos ",
        placeholder="Escribe para buscar...",
    )

    # Buscar si hay query O si hay categorías seleccionadas
    should_search = (query and len(query) >= MIN_CHARS) or (category_ids and len(category_ids) > 0)
    
    if should_search:
        now = time.time() * 1000

        if now - st.session_state.last_input_time > DEBOUNCE_MS:
            st.session_state.last_input_time = now
            nuevas_opciones = get_products(
                search=query if query and len(query) >= MIN_CHARS else None,
                category_id=category_ids  # Pasas la lista completa
            )
            
            if nuevas_opciones:
                st.session_state.product_options = nuevas_opciones

    if st.session_state.product_options:
        seleccionados = box.multiselect(
            "Productos Encontrados:",
            options=st.session_state.product_options,
            default=st.session_state.product_selections,
            format_func=lambda x: f"{x['name']} - {x['product_id'][-3:]}",
            key="product_multiselect",
            help="Selecciona ninguno o más productos",
            placeholder="Desplegar productos"
        )
        
        st.session_state.product_selections = seleccionados

        if seleccionados:
            return [item["product_id"] for item in seleccionados]

    return []