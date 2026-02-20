
import streamlit as st

from api.api_client import ApiClient

client = ApiClient()

@st.cache_data(ttl=3600)
def get_stores():
    try:
        return client.get("store")
    except Exception as e:
        st.error(f"Error: {e}")
        return []
