import time 
import requests
import streamlit as st
import os

BASE_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

@st.cache_data(ttl=300)
def get_products():
    try:
        response = requests.get(f"{BASE_URL}/products/id-names")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return []

    return []


@st.cache_data(ttl=3600)
def get_stores():
    try:
        response = requests.get(f"{BASE_URL}/store")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return []

@st.cache_data(ttl=3600)
def get_categories():
    try:
        response = requests.get(f"{BASE_URL}/products/categories")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# TO DO: Implementar llamada a API real
def get_total_sales_data() -> dict[str, int]:
    time.sleep(5)

    return {"sales": 1000, "transactions": 100, "ticket_promedio": 100}