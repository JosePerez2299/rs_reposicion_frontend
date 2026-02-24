import streamlit as st
from api.sales import get_sales_by_products_store
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render(filters):
    stores = filters.get("stores", [])
    products = filters.get("products", [])
    dates = filters.get("dates", {})

    st.title("📊 Comparativas por Producto y Tienda")

    top_products = get_sales_by_products_store(products, stores, dates)
    df_raw = pd.DataFrame(top_products)

    if df_raw.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        return

    df_raw["margin"] = df_raw["price"] - df_raw["cost"]
    df_raw["margin_pct"] = (df_raw["margin"] / df_raw["price"] * 100).round(2)
    df_raw["avg_ticket"] = (df_raw["price"] / df_raw["transactions"]).round(2)

    # ─────────────────────────────────────────────
    # KPIs GLOBALES
    # ─────────────────────────────────────────────
    total_ventas = df_raw["price"].sum()
    total_units = df_raw["qty_sold"].sum()
    total_tx = df_raw["transactions"].sum()
    avg_margin = df_raw["margin_pct"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Ventas Totales", f"${total_ventas:,.0f}")
    c2.metric("📦 Unidades Totales", f"{total_units:,.0f}")
    c3.metric("🧾 Transacciones", f"{total_tx:,.0f}")
    c4.metric("📈 Margen Promedio", f"{avg_margin:.1f}%")

    st.divider()

    # ─────────────────────────────────────────────
    # MATRIZ HEATMAP — tabs para cada métrica
    # ─────────────────────────────────────────────
    st.subheader("🗂️ Matriz Producto × Tienda")

    tab_ventas, tab_units = st.tabs(["💰 Ventas ($)", "📦 Unidades vendidas"])

    for tab, metric, fmt, colorscale in [
        (tab_ventas, "price", ",.0f", "YlGn"),
        (tab_units, "qty_sold", ",.0f", "Blues"),
    ]:
        with tab:
            matrix = df_raw.pivot_table(
                index="product_name",
                columns="store_name",
                values=metric,
                aggfunc="sum"
            ).fillna(0)

            # Agregar totales
            matrix["TOTAL"] = matrix.sum(axis=1)
            matrix.loc["TOTAL"] = matrix.sum()

            fig_hm = go.Figure(data=go.Heatmap(
                z=matrix.values,
                x=matrix.columns.tolist(),
                y=[p[:40] for p in matrix.index.tolist()],
                colorscale=colorscale,
                hovertemplate="<b>Tienda:</b> %{x}<br><b>Producto:</b> %{y}<br><b>Valor:</b> %{z:,.0f}<extra></extra>",
                text=matrix.values,
                texttemplate="%{z:,.0f}",
                showscale=True,
            ))
            fig_hm.update_layout(
                height=300 + len(matrix.index) * 45,
                xaxis_title="Tienda",
                yaxis_title="Producto",
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig_hm, use_container_width=True)

    st.divider()

    # ─────────────────────────────────────────────
    # BARRAS — Ventas y Unidades por Tienda (sin lag)
    # ─────────────────────────────────────────────
    st.subheader("📊 Ventas y Unidades por Tienda")

    barmode = "group" if st.radio("Vista", ["Agrupado", "Apilado"], horizontal=True) == "Agrupado" else "relative"

    colors = px.colors.qualitative.Set2
    product_names = df_raw["product_name"].unique()

    # Construir trazas una sola vez
    traces_ventas = []
    traces_units = []

    for i, product in enumerate(product_names):
        df_p = df_raw[df_raw["product_name"] == product].sort_values("store_name")
        color = colors[i % len(colors)]

        traces_ventas.append(go.Bar(
            name=product[:30],
            x=df_p["store_name"],
            y=df_p["price"],
            marker_color=color,
            legendgroup=product,
            hovertemplate="<b>%{x}</b><br>Ventas: $%{y:,.0f}<extra></extra>",
        ))
        traces_units.append(go.Bar(
            name=product[:30],
            x=df_p["store_name"],
            y=df_p["qty_sold"],
            marker_color=color,
            legendgroup=product,
            showlegend=False,
            hovertemplate="<b>%{x}</b><br>Unidades: %{y:,.0f}<extra></extra>",
        ))

    fig_dual = make_subplots(
        rows=1, cols=2,
        subplot_titles=("💰 Ventas ($)", "📦 Unidades vendidas"),
    )

    for t in traces_ventas:
        fig_dual.add_trace(t, row=1, col=1)
    for t in traces_units:
        fig_dual.add_trace(t, row=1, col=2)

    # Solo barmode cambia según el radio, las trazas no se reconstruyen
    fig_dual.update_layout(
        barmode=barmode,
        height=440,
        legend=dict(
            orientation="v",       # vertical
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,                # justo a la derecha del gráfico
        ),
        margin=dict(l=10, r=150, t=40, b=10),  # r más grande para dar espacio a la leyenda
    )
    fig_dual.update_yaxes(title_text="Ventas ($)", row=1, col=1)
    fig_dual.update_yaxes(title_text="Unidades", row=1, col=2)

    st.plotly_chart(fig_dual, use_container_width=True)


    # ─────────────────────────────────────────────
    # DONUT — Participación por Tienda o Producto
    # ─────────────────────────────────────────────
    st.subheader("🍩 Participación")

    col_left, col_right = st.columns(2)

    with col_left:
        segmento = st.radio("Agrupar por", ["Tienda", "Producto"], horizontal=True, key="donut_seg")

    with col_right:
        metrica_donut = st.radio("Métrica", ["Ventas ($)", "Unidades"], horizontal=True, key="donut_metric")

    group_col = "store_name" if segmento == "Tienda" else "product_name"
    value_col = "price" if metrica_donut == "Ventas ($)" else "qty_sold"
    hover_fmt = "$%{value:,.0f}" if metrica_donut == "Ventas ($)" else "%{value:,.0f} u"

    donut_df = df_raw.groupby(group_col)[value_col].sum().reset_index()
    donut_df = donut_df.sort_values(value_col, ascending=False)

    fig_donut = go.Figure(data=go.Pie(
        labels=donut_df[group_col],
        values=donut_df[value_col],
        hole=0.55,
        hovertemplate=f"<b>%{{label}}</b><br>{metrica_donut}: {hover_fmt}<br>Participación: %{{percent}}<extra></extra>",
        textinfo="label+percent",
        textposition="outside",
        marker=dict(colors=px.colors.qualitative.Set2),
    ))

    total_val = donut_df[value_col].sum()
    total_fmt = f"${total_val:,.0f}" if metrica_donut == "Ventas ($)" else f"{total_val:,.0f} u"

    fig_donut.update_layout(
        annotations=[dict(
            text=f"<b>{total_fmt}</b>",
            x=0.5, y=0.5,
            font_size=14,
            showarrow=False,
        )],
        height=420,
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=20),
    )

    st.plotly_chart(fig_donut, use_container_width=True)

    st.divider()

    # ─────────────────────────────────────────────
    # RANKING TABLA FINAL
    # ─────────────────────────────────────────────
    st.subheader("🏆 Ranking de Tiendas")

    store_summary = df_raw.groupby("store_name").agg(
        Ventas=("price", "sum"),
        Unidades=("qty_sold", "sum"),
        Transacciones=("transactions", "sum"),
        Margen_pct=("margin_pct", "mean"),
    ).reset_index()

    store_summary["Ticket Prom."] = (store_summary["Ventas"] / store_summary["Transacciones"]).round(0)

    rank_df = store_summary.sort_values("Ventas", ascending=False).reset_index(drop=True)
    rank_df.index += 1
    rank_df["Ventas"] = rank_df["Ventas"].map("${:,.0f}".format)
    rank_df["Ticket Prom."] = rank_df["Ticket Prom."].map("${:,.0f}".format)
    rank_df["Margen_pct"] = rank_df["Margen_pct"].map("{:.1f}%".format)
    rank_df = rank_df.rename(columns={"store_name": "Tienda", "Margen_pct": "Margen %"})

    st.dataframe(rank_df, use_container_width=True)