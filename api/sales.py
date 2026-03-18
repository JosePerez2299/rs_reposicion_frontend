import time
import pandas as pd
import streamlit as st

from api.api_client import ApiClient

client = ApiClient()
base_url = client.base_url
""" Retorna datos de ventas totales """


def get_sales_summary(filters: dict) -> dict[str, int]:
    stores = filters.get("stores", [])
    products = filters.get("products", [])
    dates = filters.get("dates", {})
    time.sleep(1)

    return {"sales": 1000, "transactions": 100, "ticket_promedio": 100}


@st.cache_data(ttl=60 * 3)
def get_detail_by_product(product: str, stores: list, dates: dict) -> dict[str, int]:
    try:
        response = client.get(
            "sales/details",
            params={
                "product_code": product,
                "store_ids": stores,
                "start_date": dates["fecha_inicio"],
                "end_date": dates["fecha_fin"],
            },
        )

        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return {}


@st.cache_data(ttl=60 * 10)
def get_top_sales_products(
    products_codes: list, stores: list, dates: dict
) -> dict[str, int]:
    params = {
        "start_date": dates["fecha_inicio"],
        "end_date": dates["fecha_fin"],
    }
    body = {
        "product_codes": products_codes,
        "store_ids": stores,
    }
    try:
        response = client.post("sales/top", body=body, params=params)
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return []


@st.cache_data(ttl=60 * 10)
def get_sales_by_products_store(products: list, stores: list, dates: dict):
    df = pd.DataFrame()

    for product in products:
        df_product_detail = pd.DataFrame(
            st.session_state.sales_detail[product])
        if df_product_detail.empty:
            continue
        # Group by store_name and sum qty_sold, price, cost
        group_by_store = (
            df_product_detail.groupby("store_name")
            .agg(
                {
                    "qty_sold": "sum",
                    "price": "sum",
                    "cost": "sum",
                    "transactions": "sum",
                }
            )
            .reset_index()
        )
        # Add product_name column
        group_by_store["product_name"] = product
        df = pd.concat([df, group_by_store], ignore_index=True)

    if df.empty:
        return df

    # Reorder columns to have product_name first
    df = df[["product_name", "store_name",
             "qty_sold", "price", "cost", "transactions"]]
    return df


@st.cache_data(ttl=60 * 10)
def get_products_details(
    product_codes: list,
    store_ids: list,
    dates: dict,
) -> pd.DataFrame:
    """
    Obtiene los detalles de los productos seleccionados.

    Args:
        product_codes (list): Lista de códigos de productos.
        store_ids (list): Lista de IDs de tiendas.
        dates (dict): Diccionario con las fechas de inicio y fin.

    Returns:
        pd.DataFrame: DataFrame con los detalles de los productos.
    """
    params = {
        "start_date": dates["fecha_inicio"],
        "end_date": dates["fecha_fin"],
    }
    body = {
        "product_codes": product_codes,
        "store_ids": store_ids,
    }
    try:
        response = client.post(
            "sales/products-details", body=body, params=params)

        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return []


@st.cache_data(ttl=60 * 10)
def get_all_products_details(
    store_ids: list,
    category_id: str,
    group_ids: list,
    subgroup_ids: list,
    dates_selected: dict,
    limit: int = 1000
):
    """
    Obtiene un preview de los detalles de todos los productos.

    Args:
        store_ids (list): Lista de IDs de tiendas.
        category_id (str): ID de la categoría.
        group_ids (list): Lista de IDs de grupos.
        subgroup_ids (list): Lista de IDs de subgrupos.
        dates_selected (dict): Diccionario con las fechas de inicio y fin.
        limit (int): Límite de registros a retornar.

    Returns:
        pd.DataFrame: DataFrame con los detalles de todos los productos.
    """
    params = {
        "start_date": dates_selected["fecha_inicio"],
        "end_date": dates_selected["fecha_fin"],
        "limit": limit
    }
    body = {
        "store_ids": store_ids,
        "category_id": category_id,
        "group_ids": group_ids,
        "subgroup_ids": subgroup_ids,

    }
    try:
        response = client.post("sales/all-details", body=body, params=params)
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return []


def prepare_export_all_products_details(
    store_ids: list,
    category_id: str,
    group_ids: list,
    subgroup_ids: list,
    dates_selected: dict,
):
    params = {
        "start_date": dates_selected["fecha_inicio"],
        "end_date": dates_selected["fecha_fin"],
    }
    body = {
        "store_ids": store_ids,
        "category_id": category_id,
        "group_ids": group_ids,
        "subgroup_ids": subgroup_ids,

    }

    try:
        response = client.post(
            "sales/all-details/export/prepare", body=body, params=params)
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return []


def get_export_all_products_details(token):
    try:
        response = client.get("sales/all-details/export",
                              params={"token": token})
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return []
