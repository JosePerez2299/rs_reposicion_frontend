import streamlit as st
import pandas as pd
from io import BytesIO
from api import sales
from api.api_client import base_url

COLUMN_MAPPING = {
    'product_id': 'Código Producto',
    'product_name': 'Producto',
    'category_id': 'ID Categoría',
    'category_name': 'Categoría',
    'group_id': 'ID Grupo',
    'group_name': 'Grupo',
    'subgroup_id': 'ID Subgrupo',
    'subgroup_name': 'Subgrupo',
    'store_id': 'ID Tienda',
    'store_name': 'Tienda',
    'price': 'Precio',
    'cost': 'Costo',
    'qty_sold': 'Ventas',
    'qty_stock': 'Stock',
    'qty_stock_until_date': 'Stock hasta fecha',
    'total_buy': 'Compras',
    'rotation': 'Rotación',
    'transactions': 'Transacciones',
}


def render(filtros):
    dates_selected = filtros["dates"]
    stores_selected = filtros["store_ids"]
    products_selected = filtros["product_codes"]
    category_id = filtros["category_id"]
    group_ids = filtros["group_ids"]
    subgroup_ids = filtros["subgroup_ids"]
    all_products = filtros["all_products"]

    if all_products:
        data = sales.get_all_products_details(
            store_ids=stores_selected,
            category_id=category_id,
            group_ids=group_ids,
            subgroup_ids=subgroup_ids,
            dates_selected=dates_selected
        )
    else:
        data = sales.get_products_details(
            products_selected, stores_selected, dates_selected
        )

    # --- Dataframe ---
    if data and len(data) > 0:
        df = pd.DataFrame(data).rename(columns=COLUMN_MAPPING)
        df = df[[col for col in COLUMN_MAPPING.values() if col in df.columns]] 
        st.dataframe(df)
    else:
        st.info("No hay datos para mostrar.")
        return

    # --- Descarga ---
    if all_products:
        st.info("Solo se muestran los primeros 1000 registros. Para ver todos descargue el archivo Excel.")

        if st.button("Generar archivo Excel"):
            with st.spinner("Generando archivo..."):
                try:
                    response = sales.prepare_export_all_products_details(
                        store_ids=stores_selected,
                        category_id=category_id,
                        group_ids=group_ids,
                        subgroup_ids=subgroup_ids,
                        dates_selected=dates_selected
                    )
                    token = response.get("token")
                    if token:
                        print(base_url)
                        st.success("Archivo listo.")
                        st.link_button(
                            "⬇️ Descargar Excel",
                            url=f"{base_url}/sales/all-details/export/{token}"
                        )
                    else:
                        st.error("No se pudo obtener el token.")
                except Exception:
                    st.error("No se pudo generar el archivo.")
    else:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Datos")
        buffer.seek(0)

        st.download_button(
            label="⬇️ Descargar Excel",
            data=buffer,
            file_name="datos_crudos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )