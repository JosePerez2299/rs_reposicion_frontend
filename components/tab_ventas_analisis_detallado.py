import streamlit as st
import pandas as pd


def render(filters): 
    dates = filters['dates']
    stores = filters['stores']
    products = filters['products'] 

    st.header("Análisis Detallado por Producto")
    st.divider()
    
    with st.expander("Filtros aplicados", expanded=False):
        st.write(f"Periodo: {dates['fecha_inicio']} al {dates['fecha_fin']}")
        st.write(f"Tiendas: {stores}")
        st.write(f"Productos: {products}")
    