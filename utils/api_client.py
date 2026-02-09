import requests
import streamlit as st
import os

BASE_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

@st.cache_data(ttl=300)
def get_products():
    try:
        response = requests.get(f"{BASE_URL}/products")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return []

@st.cache_data(ttl=300)
def get_stores():
    try:
        response = requests.get(f"{BASE_URL}/store")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return []
