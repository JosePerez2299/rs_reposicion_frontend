from typing import List
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from api.products import get_all_groups, get_all_subgroups, get_categories, get_products
from api.stores import get_stores
from schemas.products import Group, Subgroup


def render():

    if "analisis_ventas_filters" not in st.session_state:
        st.session_state.analisis_ventas_filters = {}
    
    filters = {
        "date": {},
        "product_codes": [],
        "store_ids": [],
        "category": None,
        "groups": None,
        "subgroups": None,
    }

    # region --------Filtro por fechas---------
    hoy = date.today()
    ayer = hoy - timedelta(days=1)
    max_pasado = hoy - timedelta(days=180)

    fechas = st.sidebar.date_input(
        "Fecha",
        key="fechas_analisis_ventas",
        value=(hoy - timedelta(days=30), ayer),
        min_value=max_pasado,
        max_value=ayer,
        format="DD/MM/YYYY",
        help="Selecciona un rango de fechas (máximo 180 días) o un solo día",
    )

    if len(fechas) == 2:
        dias_rango = (fechas[1] - fechas[0]).days + 1
        st.sidebar.info(f"Seleccionando {dias_rango} días")
    elif len(fechas) == 1:
        st.sidebar.info(f"Seleccionando 1 día")

    filters["date"] = date_filter(fechas)

    # endregion

    # region --------Filtro por tiendas---------
    stores = get_stores()
    selected_stores = st.sidebar.multiselect(
        "Tiendas",
        stores,
        format_func=lambda x: x["name"],
        placeholder="Seleccione una o más tiendas",
    )

    filters["store_ids"] = [store["id"] for store in selected_stores]

 

    # endregion

    # region --------Filtro por categorías---------
    categories = get_categories()

    st.sidebar.subheader("Categorías")

    filters["category"] = st.sidebar.selectbox(
        "Categoría",
        categories,
        index=None,
        placeholder="Seleccione una categoria",
        format_func=lambda x: x["name"],
    )
    # endregion

    # region --------Filtro por productos---------
    products = get_products()
    groups: List[Group] = get_all_groups()
    subgroups: List[Subgroup] = get_all_subgroups()
    df_products = pd.DataFrame(products)
    df_products_filtered = df_products

    if filters["category"]:
        df_groups = pd.DataFrame(groups)
        df_products_filtered = df_products_filtered[
            df_products_filtered["category_id"] == filters["category"]["id"]
        ]

        filtered_groups = df_groups[
            df_groups["category_id"] == filters["category"]["id"]
        ].to_dict(orient="records")

        filters["groups"] = st.sidebar.selectbox(
            "Grupo",
            filtered_groups,
            index=None,
            placeholder="Seleccione un grupo",
            format_func=lambda x: x["name"],
        )

        if filters["groups"]:
            df_products_filtered = df_products_filtered[
                df_products_filtered["group_id"] == filters["groups"]["id"]
            ]

            df_subgroups = pd.DataFrame(subgroups)
            filtered_subgroups = df_subgroups[
                df_subgroups["group_id"] == filters["groups"]["id"]
            ].to_dict(orient="records")

            selected_subgroups = st.sidebar.multiselect(
                "Subgrupo",
                filtered_subgroups,
                placeholder="Seleccione un subgrupo",
                format_func=lambda x: x["name"],
            )

            if len(selected_subgroups) == len(filtered_subgroups):
                filters["subgroups"] = None
            else:
                filters["subgroups"] = selected_subgroups

            if filters["subgroups"]:
                df_products_filtered = df_products_filtered[
                    df_products_filtered["subgroup_id"].isin(
                        [subgroup["id"] for subgroup in filters["subgroups"]]
                    )
                ]


    filtered_products = df_products_filtered.to_dict(orient="records")


    modo = st.sidebar.radio(
        "Modo",
        ["Seleccionar todos", "Buscar productos"],
        horizontal=True,
    )   

    if modo == "Seleccionar todos":
        filters["product_codes"] = "ALL_PRODUCTS"
    else:
        products_selected = st.sidebar.multiselect(
            "Producto" + " (Total: " + str(len(filtered_products)) + ")",
            filtered_products,
            placeholder="Seleccione un producto",
            format_func=lambda x: x["name"],
            max_selections=200,
        )
        if len(products_selected) == 0:
            st.warning("Debe seleccionar al menos un producto")

        else:
            filters["product_codes"] = [product["code"] for product in products_selected]
            st.sidebar.info(f"{len(products_selected)} productos seleccionados")
    
    if filters["product_codes"]:
        apply_button = st.sidebar.button("Aplicar", type="primary")
    else:
        apply_button = False

    if apply_button:
        st.session_state.analisis_ventas_filters_changed = True
        st.toast("Se aplicaron los filtros", icon="✅", duration=300, )
        st.session_state.analisis_ventas_filters = filters
        


def date_filter(fechas):
    filter_data = {}
    # Manejar tanto un solo día como un rango
    if isinstance(fechas, tuple):
        if len(fechas) == 2:
            # Rango de fechas
            filter_data["fecha_inicio"] = fechas[0].isoformat()
            filter_data["fecha_fin"] = fechas[1].isoformat()
        elif len(fechas) == 1:
            # Un solo día (usar el mismo día como inicio y fin)
            filter_data["fecha_inicio"] = fechas[0].isoformat()
            filter_data["fecha_fin"] = fechas[0].isoformat()
    elif isinstance(fechas, date):
        # Por si acaso devuelve un solo date object
        filter_data["fecha_inicio"] = fechas.isoformat()
        filter_data["fecha_fin"] = fechas.isoformat()

    return filter_data
