import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import api.sales as api_sales


def _get_stock_indicators(df: pd.DataFrame, dias_periodo: int) -> dict:
    """Calcula indicadores de stock para el label del expander."""
    if df.empty or "stock" not in df.columns:
        return {"negro": 0, "rojo": 0, "amarillo": 0, "verde": 0}

    conteos = {"negro": 0, "rojo": 0, "amarillo": 0, "verde": 0}

    for _, row in df.iterrows():
        stock = row.get("stock", 0)
        qty_sold = row.get("qty_sold", 0)

        if stock == 0:
            conteos["negro"] += 1
        elif qty_sold <= 0:  # FIX: cubre negativos y cero
            conteos["amarillo"] += 1
        else:
            if dias_periodo > 0:
                ventas_dia = qty_sold / dias_periodo
                dias_restantes = stock / ventas_dia if ventas_dia > 0 else None
            else:
                dias_restantes = None

            if dias_restantes is not None and dias_restantes < 7:
                conteos["rojo"] += 1
            elif stock < 6 or (dias_restantes is not None and dias_restantes < 14):
                conteos["amarillo"] += 1
            else:
                conteos["verde"] += 1

    return conteos


def _build_expander_label(product: str, df: pd.DataFrame, dias_periodo: int) -> str:
    """Construye el label enriquecido del expander."""
    if df is None or df.empty:
        return f"**{product}** — Sin datos"

    total_qty   = int(df["qty_sold"].sum()) if "qty_sold" in df.columns else 0
    total_price = df["price"].sum() if "price" in df.columns else 0
    total_stock = int(df["stock"].sum()) if "stock" in df.columns else 0

    indicadores = _get_stock_indicators(df, dias_periodo)

    stock_parts = []
    if indicadores["negro"]   > 0: stock_parts.append(f"⚫{indicadores['negro']}")
    if indicadores["rojo"]    > 0: stock_parts.append(f"🔴{indicadores['rojo']}")
    if indicadores["amarillo"]> 0: stock_parts.append(f"🟡{indicadores['amarillo']}")
    if indicadores["verde"]   > 0: stock_parts.append(f"🟢{indicadores['verde']}")
    stock_str = " ".join(stock_parts) if stock_parts else "—"

    return (
        f"**{product}**"
        f"　｜　{stock_str}"
        f"　｜　📦 Stock: {total_stock:,}"
        f"　｜　🛒 Vendido: {total_qty:,} uds"
        f"　｜　💰 ${total_price:,.0f}"
    )


def render(filters):
    dates = filters["dates"]
    stores = filters["stores"]
    products = filters["products"]
    
    st.header("Análisis Detallado por Producto")
    if not products:
        st.write("No hay productos seleccionados")
        return

    dias_periodo = 0
    fecha_fin = None
    if dates and "fecha_inicio" in dates and "fecha_fin" in dates:
        try:
            fecha_inicio = datetime.strptime(dates["fecha_inicio"], "%Y-%m-%d")
            fecha_fin    = datetime.strptime(dates["fecha_fin"], "%Y-%m-%d")
            dias_periodo = (fecha_fin - fecha_inicio).days + 1
        except (KeyError, TypeError, AttributeError, ValueError):
            pass
    
    st.session_state["sales_detail"] = {}

    for index, product in enumerate(products):

        reset_key = f"reset_counter_{index}"
        if reset_key not in st.session_state:
            st.session_state[reset_key] = 0
        rev = st.session_state[reset_key]

        # Cargar datos antes del expander para poder usarlos en el label
        sales_detail = api_sales.get_detail_by_product(product, stores, dates)
        st.session_state["sales_detail"][product] = sales_detail
        df_raw = pd.DataFrame(sales_detail) if sales_detail else pd.DataFrame()
        
        label = _build_expander_label(sales_detail[0]["product_name"], df_raw, dias_periodo)

        with st.expander(label=label, expanded=(index == 0)):
            subtab1, subtab2, subtab3 = st.tabs(
                ["🏪 Por Tienda", "📅 Evolución", "📊 Stats"]
            )
            with subtab1:
                if df_raw.empty:
                    st.write("No hay datos para mostrar")
                    continue

                df = df_raw.copy()

                with st.expander("Filtros", expanded=False):
                    col_f1, col_f2, col_f3 = st.columns([3, 3, 1])
                    with col_f1:
                        selected_stores = st.multiselect(
                            "Selecciona las tiendas",
                            df["store_name"].unique() if "store_name" in df.columns else [],
                            key=f"stores_{index}_{rev}",
                        )
                    with col_f2:
                        products_ids = st.multiselect(
                            "Selecciona las variantes",
                            sorted(df["product_id"].unique()) if "product_id" in df.columns else [],
                            format_func=lambda x: f"{x[-3:]}",
                            key=f"products_{index}_{rev}",
                        )
                    with col_f3:
                        st.write("")
                        st.write("")
                        if st.button("🧹 Limpiar", key=f"clear_{index}"):
                            st.session_state[reset_key] += 1
                            st.rerun()

                    col_f4, col_f5, col_f6, col_f7 = st.columns(4)

                    # --- STOCK ---
                    with col_f4:
                        stock_min_active = st.checkbox(
                            "Stock mínimo",
                            value=False,
                            key=f"stock_min_active_{index}_{rev}",
                        )
                        stock_min = st.number_input(
                            "Valor",
                            min_value=None,
                            value=0,
                            step=1,
                            key=f"stock_min_{index}_{rev}",
                            disabled=not stock_min_active,
                            label_visibility="collapsed",
                        )

                    with col_f5:
                        stock_max_active = st.checkbox(
                            "Stock máximo",
                            value=False,
                            key=f"stock_max_active_{index}_{rev}",
                        )
                        stock_max = st.number_input(
                            "Valor",
                            min_value=None,
                            value=99999,
                            step=1,
                            key=f"stock_max_{index}_{rev}",
                            disabled=not stock_max_active,
                            label_visibility="collapsed",
                        )

                    # --- VENTAS ---
                    with col_f6:
                        qty_min_active = st.checkbox(
                            "Ventas mínimas",
                            value=False,
                            key=f"qty_min_active_{index}_{rev}",
                        )
                        qty_min = st.number_input(
                            "Valor",
                            min_value=None,
                            value=0,
                            step=1,
                            key=f"qty_min_{index}_{rev}",
                            disabled=not qty_min_active,
                            label_visibility="collapsed",
                        )

                    with col_f7:
                        qty_max_active = st.checkbox(
                            "Ventas máximas",
                            value=False,
                            key=f"qty_max_active_{index}_{rev}",
                        )
                        qty_max = st.number_input(
                            "Valor",
                            min_value=None,
                            value=99999,
                            step=1,
                            key=f"qty_max_{index}_{rev}",
                            disabled=not qty_max_active,
                            label_visibility="collapsed",
                        )

                # --- APLICAR FILTROS ---
                filtered_df = df.copy()

                # Filtros de tienda y variante (siempre activos si hay selección)
                if selected_stores:
                    filtered_df = filtered_df[filtered_df["store_name"].isin(selected_stores)]
                if products_ids:
                    filtered_df = filtered_df[filtered_df["product_id"].isin(products_ids)]

                # Filtros numéricos: solo se aplican si el checkbox está activo
                if stock_min_active:
                    filtered_df = filtered_df[filtered_df["stock"] >= stock_min]
                if stock_max_active:
                    filtered_df = filtered_df[filtered_df["stock"] <= stock_max]
                if qty_min_active:
                    filtered_df = filtered_df[filtered_df["qty_sold"] >= qty_min]
                if qty_max_active:
                    filtered_df = filtered_df[filtered_df["qty_sold"] <= qty_max]

                # --- RESUMEN ---
                total_ventas        = filtered_df["qty_sold"].sum()
                total_transacciones = filtered_df["transactions"].sum()
                total_stock         = filtered_df["stock"].sum()
                total_monto         = filtered_df["price"].sum()
                ventas_promedio_dia_total = (total_ventas / dias_periodo) if dias_periodo > 0 else 0

                st.subheader("Resumen")
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1: st.metric("Unidades Vendidas", f"{total_ventas:,.0f}")
                with col2: st.metric("Transacciones", f"{total_transacciones:,.0f}")
                with col3: st.metric("Stock Total", f"{total_stock:,.0f}")
                with col4: st.metric("Monto Total", f"${total_monto:,.2f}")
                with col5:
                    st.metric(
                        "Ventas Promedio / Día",
                        f"{ventas_promedio_dia_total:.1f}" if dias_periodo > 0 else "—",
                    )
                with col6:
                    st.metric(
                        "Días del Período",
                        f"{dias_periodo:,.0f}" if dias_periodo > 0 else "—",
                    )

                # --- COLUMNAS CALCULADAS ---
                if not filtered_df.empty:
                    ventas_promedio_dia = (
                        (filtered_df["qty_sold"] / dias_periodo).round(2)
                        if dias_periodo > 0
                        else pd.Series(0, index=filtered_df.index)
                    )
                    dias_stock = filtered_df.apply(
                        lambda row: (
                            round(row["stock"] / (row["qty_sold"] / dias_periodo), 1)
                            if dias_periodo > 0 and row["qty_sold"] > 0  # FIX: > 0 excluye negativos
                            else None
                        ),
                        axis=1,
                    )

                    def icono_stock(stock, ventas, dias):
                        if stock == 0:    return "⚫"
                        elif ventas <= 0: return "⚪"  # FIX: <= 0 cubre ventas negativas
                        elif stock < 3 or (dias is not None and dias < 7):  return "🔴"
                        elif stock < 6 or (dias is not None and dias < 14): return "🟡"
                        else: return "🟢"

                    def formato_stock(row):
                        ventas = ventas_promedio_dia[row.name]
                        dias   = dias_stock[row.name]
                        icono  = icono_stock(row["stock"], ventas, dias)
                        return f"{int(row['stock'])} {icono}"

                    def formato_proyeccion(row):
                        ventas = ventas_promedio_dia[row.name]
                        dias   = dias_stock[row.name]
                        stock  = row["stock"]

                        if stock == 0:   return "⚫ Sin stock"
                        if ventas <= 0:  return "⚪ Sin movimiento"  # FIX: <= 0 cubre ventas negativas
                        if dias is None or fecha_fin is None: return "—"

                        # FIX: guard contra NaN, infinito o valores negativos en dias
                        if not isinstance(dias, (int, float)) or pd.isna(dias) or dias < 0:
                            return "—"

                        fecha_quiebre = fecha_fin + timedelta(days=int(dias))
                        fecha_str = f"{fecha_quiebre.day} {fecha_quiebre.strftime('%b')}"

                        if dias < 7:    return f"🔴 Quiebre ~{fecha_str}"
                        elif dias < 14: return f"🟡 Quiebre ~{fecha_str}"
                        else:           return f"🟢 Quiebre ~{fecha_str}"

                    display_df = filtered_df.copy()
                    cols_to_drop = [c for c in ["store_id"] if c in display_df.columns]
                    display_df = display_df.drop(columns=cols_to_drop)

                    display_df["stock"]      = filtered_df.apply(formato_stock, axis=1)
                    display_df["rotation"]   = filtered_df["rotation"].apply(lambda x: f"{x:.2f}%")
                    display_df["proyección"] = filtered_df.apply(formato_proyeccion, axis=1)

                    col_order = ["product_id", "store_name", "qty_sold", "buy_qty", "stock", "rotation", "transactions", "price", "cost", "proyección"]
                    col_order = [c for c in col_order if c in display_df.columns]
                    display_df = display_df[col_order]

                    st.dataframe(display_df, width="stretch")
                else:
                    st.dataframe(filtered_df, width="stretch")