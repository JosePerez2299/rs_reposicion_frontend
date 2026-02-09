import streamlit as st

st.set_page_config(
    page_title="Mi App",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Bienvenido a Mi Aplicación")
st.write("Usa el menú lateral para navegar")

st.markdown("""
### Páginas disponibles:
- 📊 **Dashboard**: Visualiza tus datos
- 🔍 **Filtros**: Aplica filtros personalizados
- ⚙️ **Configuración**: Ajusta la aplicación
""")