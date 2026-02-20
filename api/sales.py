# TO DO: Implementar llamada a API real
import time
import pandas as pd
import streamlit as st

from api.api_client import ApiClient

client = ApiClient()

""" Retorna datos de ventas totales """


def get_sales_summary(filters: dict) -> dict[str, int]:
    stores = filters.get("stores", [])
    products = filters.get("products", [])
    dates = filters.get("dates", {})
    time.sleep(1)

    return {"sales": 1000, "transactions": 100, "ticket_promedio": 100}


@st.cache_data(ttl=30 * 60)
def get_detail_by_product(product: str, stores: list, dates: dict) -> dict[str, int]:

    response = client.get(
        "sales/summary",
        params={
            "product_name": product,
            "stores": stores,
            "start_date": dates["fecha_inicio"],
            "end_date": dates["fecha_fin"],
        },
    )

    print(response)
    return response
