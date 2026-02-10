import streamlit as st

st.set_page_config(
    page_title="Mi App",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)



st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)
st.title("Bienvenido a Mi Aplicación")
st.write("Usa el menú lateral para navegar")


st.markdown("""
### Páginas disponibles:
- 📊 **Dashboard**: Visualiza tus datos
- 🔍 **Filtros**: Aplica filtros personalizados
- ⚙️ **Configuración**: Ajusta la aplicación
""")