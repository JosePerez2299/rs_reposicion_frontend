import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ============= SIMULACIÓN DE RESPUESTA DEL BACKEND =============
def get_sales_data(filters):
    """
    Simula la respuesta de tu backend con fact_daily_sales
    """
    np.random.seed(42)
    
    # Generar fechas en el rango
    fecha_inicio = datetime.strptime(filters["dates"]["fecha_inicio"], "%Y-%m-%d")
    fecha_fin = datetime.strptime(filters["dates"]["fecha_fin"], "%Y-%m-%d")
    
    # Data dummy
    productos = filters["products"] if filters["products"] else ["BOLSO EPONA - NAVY/PURPLE", "CARTERA MINIMAL - BLACK"]
    tiendas = filters["stores"] if filters["stores"] else [101, 301]
    tallas = ["S", "M", "L", "XL", "UNICA"]
    
    data = []
    for producto in productos:
        for tienda in tiendas:
            for talla in tallas:
                # Generar ventas aleatorias por día
                dias = (fecha_fin - fecha_inicio).days + 1
                for i in range(dias):
                    fecha = fecha_inicio + timedelta(days=i)
                    
                    # Algunas combinaciones no tienen ventas
                    if np.random.random() > 0.3:
                        ventas = np.random.randint(500, 5000)
                        transacciones = np.random.randint(5, 50)
                        
                        data.append({
                            "fecha": fecha.strftime("%Y-%m-%d"),
                            "producto": producto,
                            "tienda_id": tienda,
                            "tienda_nombre": f"Tienda {tienda}",
                            "talla": talla,
                            "ventas": ventas,
                            "transacciones": transacciones
                        })
    
    return pd.DataFrame(data)


# ============= FUNCIONES DE AGREGACIÓN =============
def agregar_por_producto(df):
    """Agrupa por producto mostrando totales"""
    return df.groupby("producto").agg({
        "ventas": "sum",
        "transacciones": "sum"
    }).reset_index().sort_values("ventas", ascending=False)


def agregar_por_producto_tienda(df):
    """Agrupa por producto y tienda"""
    return df.groupby(["producto", "tienda_nombre"]).agg({
        "ventas": "sum",
        "transacciones": "sum"
    }).reset_index()


def agregar_por_producto_talla(df):
    """Agrupa por producto y talla (detalle expandible)"""
    return df.groupby(["producto", "talla"]).agg({
        "ventas": "sum",
        "transacciones": "sum"
    }).reset_index().sort_values(["producto", "ventas"], ascending=[True, False])


# ============= UI PRINCIPAL =============
st.title("📊 Dashboard de Ventas")

# Simular filtros aplicados (estos vendrían de tu sidebar)
filtros = {
    "dates": {"fecha_inicio": "2026-02-01", "fecha_fin": "2026-02-10"},
    "stores": [101, 301],
    "products": ["BOLSO EPONA - NAVY/PURPLE"],
    "categories": []
}

# Mostrar filtros activos
with st.expander("🔍 Filtros aplicados", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Fecha inicio:** {filtros['dates']['fecha_inicio']}")
        st.write(f"**Fecha fin:** {filtros['dates']['fecha_fin']}")
    with col2:
        st.write(f"**Tiendas:** {', '.join(map(str, filtros['stores']))}")
    with col3:
        st.write(f"**Productos:** {len(filtros['products'])} seleccionados")

# Obtener datos del backend (simulado)
with st.spinner("Cargando datos de ventas..."):
    df_raw = get_sales_data(filtros)

if df_raw.empty:
    st.warning("No se encontraron datos para los filtros seleccionados")
    st.stop()

# ============= MÉTRICAS GENERALES =============
st.subheader("📈 Resumen General")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Ventas Totales", f"${df_raw['ventas'].sum():,.0f}")
with col2:
    st.metric("Transacciones", f"{df_raw['transacciones'].sum():,}")
with col3:
    st.metric("Ticket Promedio", f"${df_raw['ventas'].sum() / df_raw['transacciones'].sum():,.2f}")
with col4:
    st.metric("Productos", len(df_raw['producto'].unique()))

st.divider()

# ============= VENTAS POR PRODUCTO =============
st.subheader("🛍️ Ventas por Producto")

df_productos = agregar_por_producto(df_raw)

# Tabla resumen
st.dataframe(
    df_productos.style.format({
        "ventas": "${:,.0f}",
        "transacciones": "{:,}"
    }),
    use_container_width=True,
    hide_index=True
)

# Gráfico de barras
st.bar_chart(df_productos.set_index("producto")["ventas"])

st.divider()

# ============= DETALLE POR PRODUCTO (EXPANDIBLE) =============
st.subheader("📦 Detalle por Producto")

for producto in df_raw['producto'].unique():
    df_producto = df_raw[df_raw['producto'] == producto]
    
    # Métricas del producto
    ventas_producto = df_producto['ventas'].sum()
    transacciones_producto = df_producto['transacciones'].sum()
    
    with st.expander(f"**{producto}** - ${ventas_producto:,.0f} | {transacciones_producto:,} transacciones"):
        
        # Tabs para diferentes vistas
        tab1, tab2, tab3 = st.tabs(["🏪 Por Tienda", "👕 Por Talla", "📅 Serie Temporal"])
        
        with tab1:
            df_tiendas = df_producto.groupby("tienda_nombre").agg({
                "ventas": "sum",
                "transacciones": "sum"
            }).reset_index()
            
            st.dataframe(
                df_tiendas.style.format({
                    "ventas": "${:,.0f}",
                    "transacciones": "{:,}"
                }),
                use_container_width=True,
                hide_index=True
            )
        
        with tab2:
            df_tallas = df_producto.groupby("talla").agg({
                "ventas": "sum",
                "transacciones": "sum"
            }).reset_index().sort_values("ventas", ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(
                    df_tallas.style.format({
                        "ventas": "${:,.0f}",
                        "transacciones": "{:,}"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            
            with col2:
                st.bar_chart(df_tallas.set_index("talla")["ventas"])
        
        with tab3:
            df_temporal = df_producto.groupby("fecha").agg({
                "ventas": "sum",
                "transacciones": "sum"
            }).reset_index()
            
            st.line_chart(df_temporal.set_index("fecha")[["ventas", "transacciones"]])

st.divider()

# ============= COMPARACIÓN DE TIENDAS =============
if len(filtros['stores']) > 1:
    st.subheader("🏪 Comparación entre Tiendas")
    
    df_tiendas_comp = df_raw.groupby("tienda_nombre").agg({
        "ventas": "sum",
        "transacciones": "sum"
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Ventas por Tienda**")
        st.bar_chart(df_tiendas_comp.set_index("tienda_nombre")["ventas"])
    
    with col2:
        st.write("**Transacciones por Tienda**")
        st.bar_chart(df_tiendas_comp.set_index("tienda_nombre")["transacciones"])

# ============= DATOS CRUDOS (OPCIONAL) =============
with st.expander("🔍 Ver datos crudos"):
    st.dataframe(df_raw, use_container_width=True)