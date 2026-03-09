import streamlit as st
import pandas as pd
from io import BytesIO
from api import sales

def render(filters):
    st.write("Datos crudos")

    stores_ids = filters.get("stores", [])
    product_codes = filters.get("products", [])
    dates = filters.get("dates", [])
    data = sales.get_all_details(product_codes, stores_ids, dates)
    data_df = pd.DataFrame(data)

    

    data_df = data_df.rename(columns={
        "product_id": "Código Producto",
        "product_name": "Producto",
        "store_id": "Código Tienda",
        "store_name": "Tienda",
        "price": "Precio",
        "cost": "Costo",
        "qty_sold": "Cantidad Vendida",
        "transactions": "Transacciones",
        "stock": "Stock",
        "qty_buy": "Cantidad Comprada",
        "rotation": "Rotación"
    })
    st.write(data_df)

    if not data_df.empty:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            data_df.to_excel(writer, index=False, sheet_name="Datos")
        buffer.seek(0)

        st.download_button(
            label="Descargar a Excel",
            data=buffer,
            file_name="datos_crudos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )