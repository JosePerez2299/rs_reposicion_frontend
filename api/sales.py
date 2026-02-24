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


@st.cache_data(ttl=60 * 3)
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

    return response


@st.cache_data(ttl=60 * 10)
def get_top_sales_products(products: list, stores: list, dates: dict) -> dict[str, int]:
    response = client.get(
        "sales/top",
        params={
            "product_names": products,
            "store_ids": stores,
            "start_date": dates["fecha_inicio"],
            "end_date": dates["fecha_fin"],
        },
    )
    return response

@st.cache_data(ttl=60 * 10)
def get_sales_by_products_store(products: list, stores: list, dates: dict):
    df = pd.DataFrame()
    for product in products:
        df_product_detail = pd.DataFrame(st.session_state.sales_detail[product])
        if df_product_detail.empty:
            continue
        print(df_product_detail.head())
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

    # Reorder columns to have product_name first
    df = df[["product_name", "store_name", "qty_sold", "price", "cost", "transactions"]]
    return df
