
import streamlit as st
from api.api_client import ApiClient

client = ApiClient()

@st.cache_data(ttl=3000)
def get_products():
    try:
        products = client.get("products/id-names")
        return products
    except Exception as e:
        st.error(f"Error: {e}")
        return []


@st.cache_data(ttl=3600)
def get_categories() -> list[dict]:
    try:
        categories = client.get("products/categories")
        return categories
    except Exception as e:
        st.error(f"Error: {e}")
        return []


