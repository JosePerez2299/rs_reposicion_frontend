import streamlit as st

st.set_page_config(
    page_title="RS Reposición",
    page_icon="�",
    layout="wide"
)

st.write("# Sistema de Reposición y Stock 📦")

st.markdown(
    """
    Sistema frontend para la gestión de reposición y stock de productos. 
    
    **⚠️ Versión en Desarrollo**
    
    Esta es una versión preliminar donde la mayoría de módulos están deshabilitados temporalmente mientras se trabaja en su implementación.
    
    **🟢 Funcionalidad Activa:**
    - Exportación a Excel para datos de reposición y stock
    
    **🔧 Módulos en Desarrollo:**
    - Gestión de inventario
    - Reportes avanzados
    - Panel de control
    - Notificaciones automáticas
    """
)

st.info("👈 Seleccione 'Analisis de Ventas' desde el menú lateral para acceder a la funcionalidad disponible.")