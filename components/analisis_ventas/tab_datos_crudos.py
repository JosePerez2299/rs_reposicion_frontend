import streamlit as st
import pandas as pd
from io import BytesIO
from api import sales

def render(filtros):
    st.write("Datos crudos")

    dates_selected = filtros["dates"]
    stores_selected = filtros["store_ids"]
    products_selected = filtros["product_codes"]
    all_products = filtros["all_products"]

    if all_products:
        st.write("Estamos trabajando en esta sección cuando se seleccionan todos los productos")
        return
    else:
        data = sales.get_all_details(products_selected, stores_selected, dates_selected)

    data_df = pd.DataFrame(data)

    

    data_df = data_df.rename(columns={
        "product_id": "Código Producto",
        "product_name": "Producto",
        "group_id": "ID Grupo",
        "group_name": "Nombre Grupo",
        "subgroup_id": "ID Subgrupo",
        "subgroup_name": "Nombre Subgrupo",
        "department_id": "ID Departamento",
        "department_name": "Nombre Departamento",
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