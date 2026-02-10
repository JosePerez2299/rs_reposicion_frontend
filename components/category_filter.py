import streamlit as st
from utils.api_client import get_categories

def category_filter(box):
    
    if "selected_category_ids" not in st.session_state:
        st.session_state.selected_category_ids = []
    
    categorias = get_categories()
    
    if categorias:
        # Filtrar las categorías que coincidan con los IDs guardados
        preseleccionadas = [
            cat for cat in categorias 
            if cat["id"] in st.session_state.selected_category_ids
        ]
        
        seleccion = box.multiselect(
            "Categoría:",
            options=categorias,
            format_func=lambda x: x["description"],
            default=preseleccionadas,  # Objetos completos que están en opciones
            key="category_select",
            help="Selecciona ninguna o más categorías",
            placeholder="Desplegar categorías"
        )
        
        # Guarda solo los IDs
        st.session_state.selected_category_ids = [cat["id"] for cat in seleccion]
        return st.session_state.selected_category_ids
    
    return []