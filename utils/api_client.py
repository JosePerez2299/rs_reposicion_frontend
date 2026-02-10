import requests
import streamlit as st
import os

BASE_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

@st.cache_data(ttl=300)
def get_products(search: str | None = None, category_id: int | None = None, limit: int = 50):
    params = {}
    
    if search:
        params["search"] = search
    
    if category_id:
        params["category_id"] = category_id
    
    if search or category_id:
        params["limit"] = limit

        try:
            response = requests.get(f"{BASE_URL}/products", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error: {e}")
            return []

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

def get_categories():
    try:
        response = requests.get(f"{BASE_URL}/products/categories")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return []
