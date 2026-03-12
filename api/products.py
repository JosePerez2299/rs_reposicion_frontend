
import streamlit as st
from api.api_client import ApiClient
from typing import List

from schemas.products import Subgroup, Group, Category, Product
client = ApiClient()

@st.cache_data(ttl=3000)
def get_products() -> List[Product]:
    """
    Obtiene los productos.
    
    Returns:
        list[Product]: Lista de productos.
    """
    try:
        products = client.get("products/minimal")
        return products
    except Exception as e:
        st.error(f"Error: {e}")
        return []


@st.cache_data(ttl=3600)
def get_categories() -> List[Category]:
    """
    Obtiene las categorías de productos.
    
    Returns:
        list[Category]: Lista de categorías.
    """
    try:
        categories = client.get("products/categories")
        return categories
    except Exception as e:
        st.error(f"Error: {e}")
        return []



@st.cache_data(ttl=3600)
def get_all_groups() -> List[Group]:
    """
    Obtiene los grupos de un departamento.
    
    Returns:
        list[Group]: Lista de grupos.
    """
    try:
        groups = client.get("products/groups")
        return groups
    except Exception as e:
        st.error(f"Error: {e}")
        return []




@st.cache_data(ttl=3600)
def get_all_subgroups() -> List[Subgroup]:
    """
    Obtiene los subgrupos de un grupo.
    
    Returns:
        list[Subgroup]: Lista de subgrupos.
    """
    try:
        subgroups = client.get("products/subgroups")
        return subgroups
    except Exception as e:
        st.error(f"Error: {e}")
        return []



