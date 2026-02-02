# demo_dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Inventario - Demo",
    page_icon="📊",
    layout="wide"
)

# ========================================
# GENERAR DATOS DUMMY
# ========================================

@st.cache_data
def generar_datos_dummy():
    """Genera datos de ejemplo para la demo"""
    
    # Tiendas
    tiendas = ['Tienda Centro', 'Tienda Norte', 'Tienda Sur', 'Tienda Este']
    
    # Productos
    productos = [
        'Zapato Deportivo Nike Air', 'Zapato Formal Clarks', 'Sandalia Adidas',
        'Bota Timberland', 'Zapato Casual Puma', 'Sandalia Crocs',
        'Zapato Running Asics', 'Bota Dr. Martens', 'Zapato Vans Old Skool',
        'Sandalia Birkenstock', 'Zapato Converse Chuck', 'Bota Caterpillar',
        'Zapato Reebok Classic', 'Sandalia Havaianas', 'Zapato New Balance'
    ]
    
    categorias_map = {
        'Zapato Deportivo Nike Air': 'Deportivos',
        'Zapato Formal Clarks': 'Formales',
        'Sandalia Adidas': 'Sandalias',
        'Bota Timberland': 'Botas',
        'Zapato Casual Puma': 'Casuales',
        'Sandalia Crocs': 'Sandalias',
        'Zapato Running Asics': 'Deportivos',
        'Bota Dr. Martens': 'Botas',
        'Zapato Vans Old Skool': 'Casuales',
        'Sandalia Birkenstock': 'Sandalias',
        'Zapato Converse Chuck': 'Casuales',
        'Bota Caterpillar': 'Botas',
        'Zapato Reebok Classic': 'Deportivos',
        'Sandalia Havaianas': 'Sandalias',
        'Zapato New Balance': 'Deportivos'
    }
    
    # Generar datos de ventas e inventario
    data = []
    
    for tienda in tiendas:
        for producto in productos:
            # Ventas últimos 30 días (aleatorio)
            ventas_30d = np.random.randint(5, 80)
            ventas_90d = ventas_30d * 3 + np.random.randint(-20, 30)
            
            # Stock actual
            stock_actual = np.random.randint(0, 100)
            stock_minimo = np.random.randint(10, 30)
            
            # Calcular rotación (días para vender el stock actual)
            if ventas_30d > 0:
                dias_cobertura = round((stock_actual / (ventas_30d / 30)), 1)
            else:
                dias_cobertura = 999
            
            # Clasificar rotación
            if dias_cobertura < 15:
                rotacion = 'Rápida'
                color_rotacion = '🟢'
            elif dias_cobertura < 30:
                rotacion = 'Normal'
                color_rotacion = '🟡'
            elif dias_cobertura < 60:
                rotacion = 'Lenta'
                color_rotacion = '🟠'
            else:
                rotacion = 'Estancada'
                color_rotacion = '🔴'
            
            # Estado de stock
            if stock_actual == 0:
                estado_stock = 'CRÍTICO'
                color_stock = '🔴'
            elif stock_actual <= stock_minimo * 0.5:
                estado_stock = 'MUY BAJO'
                color_stock = '🟠'
            elif stock_actual <= stock_minimo:
                estado_stock = 'BAJO'
                color_stock = '🟡'
            else:
                estado_stock = 'OK'
                color_stock = '🟢'
            
            data.append({
                'Tienda': tienda,
                'Producto': producto,
                'Categoría': categorias_map[producto],
                'Ventas_30d': ventas_30d,
                'Ventas_90d': ventas_90d,
                'Stock_Actual': stock_actual,
                'Stock_Mínimo': stock_minimo,
                'Días_Cobertura': dias_cobertura if dias_cobertura < 999 else 999,
                'Rotación': rotacion,
                'Color_Rotación': color_rotacion,
                'Estado_Stock': estado_stock,
                'Color_Stock': color_stock,
                'Precio': np.random.randint(30, 150)
            })
    
    return pd.DataFrame(data)

# Cargar datos
df = generar_datos_dummy()

# ========================================
# SIDEBAR - FILTROS
# ========================================

st.sidebar.header("🔍 Filtros")

# Filtro de período
periodo = st.sidebar.selectbox(
    "Período de ventas",
    ["Últimos 30 días", "Últimos 90 días"],
    index=0
)

# Filtro de tienda
tiendas_disponibles = ['Todas'] + sorted(df['Tienda'].unique().tolist())
tienda_seleccionada = st.sidebar.selectbox(
    "Tienda",
    tiendas_disponibles
)

# Filtro de categoría
categorias_disponibles = ['Todas'] + sorted(df['Categoría'].unique().tolist())
categoria_seleccionada = st.sidebar.selectbox(
    "Categoría",
    categorias_disponibles
)

# Filtro de estado de stock
st.sidebar.markdown("---")
st.sidebar.markdown("**Alertas de Stock:**")
solo_criticos = st.sidebar.checkbox("Solo productos críticos")
solo_stock_bajo = st.sidebar.checkbox("Solo stock bajo")

# Búsqueda por nombre
st.sidebar.markdown("---")
busqueda = st.sidebar.text_input("🔍 Buscar producto", "")

# ========================================
# APLICAR FILTROS
# ========================================

df_filtrado = df.copy()

# Filtrar por tienda
if tienda_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Tienda'] == tienda_seleccionada]

# Filtrar por categoría
if categoria_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Categoría'] == categoria_seleccionada]

# Filtrar por estado de stock
if solo_criticos:
    df_filtrado = df_filtrado[df_filtrado['Estado_Stock'] == 'CRÍTICO']
elif solo_stock_bajo:
    df_filtrado = df_filtrado[df_filtrado['Estado_Stock'].isin(['CRÍTICO', 'MUY BAJO', 'BAJO'])]

# Búsqueda por nombre
if busqueda:
    df_filtrado = df_filtrado[
        df_filtrado['Producto'].str.contains(busqueda, case=False, na=False)
    ]

# Seleccionar columna de ventas según período
columna_ventas = 'Ventas_30d' if periodo == "Últimos 30 días" else 'Ventas_90d'

# ========================================
# HEADER
# ========================================

st.title("📊 Sistema de Gestión de Inventario y Ventas")
st.markdown("### Demo - Reporte de Ventas por Tienda y Producto")

# ========================================
# KPIs PRINCIPALES
# ========================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_productos = len(df_filtrado)
    st.metric("Total Productos", f"{total_productos:,}")

with col2:
    total_ventas = df_filtrado[columna_ventas].sum()
    st.metric(f"Ventas ({periodo})", f"{total_ventas:,} unidades")

with col3:
    stock_total = df_filtrado['Stock_Actual'].sum()
    st.metric("Stock Total", f"{stock_total:,} unidades")

with col4:
    productos_criticos = len(df_filtrado[df_filtrado['Estado_Stock'] == 'CRÍTICO'])
    st.metric("🔴 Stock Crítico", productos_criticos)

with col5:
    productos_bajo = len(df_filtrado[df_filtrado['Estado_Stock'].isin(['BAJO', 'MUY BAJO'])])
    st.metric("🟡 Stock Bajo", productos_bajo)

# ========================================
# ALERTAS
# ========================================

if productos_criticos > 0:
    st.error(f"⚠️ ALERTA: {productos_criticos} productos SIN STOCK")
    with st.expander("Ver productos sin stock"):
        df_criticos = df_filtrado[df_filtrado['Estado_Stock'] == 'CRÍTICO'][
            ['Tienda', 'Producto', 'Categoría', 'Stock_Actual']
        ]
        st.dataframe(df_criticos, use_container_width=True)

st.markdown("---")

# ========================================
# TABS PRINCIPALES
# ========================================

tab1, tab2, tab3 = st.tabs(["📊 Reporte Principal", "📈 Análisis de Ventas", "🔄 Rotación de Mercancía"])

# ========================================
# TAB 1: REPORTE PRINCIPAL
# ========================================

with tab1:
    st.subheader("Reporte Detallado: Ventas e Inventario")
    
    # Preparar dataframe para mostrar
    df_display = df_filtrado[[
        'Tienda', 'Producto', 'Categoría', columna_ventas, 
        'Stock_Actual', 'Stock_Mínimo', 'Rotación', 'Estado_Stock'
    ]].copy()
    
    df_display.columns = [
        'Tienda', 'Producto', 'Categoría', f'Ventas ({periodo})', 
        'Stock Actual', 'Stock Mín.', 'Rotación', 'Estado Stock'
    ]
    
    # Función para colorear filas
    def highlight_stock(row):
        if row['Estado Stock'] == 'CRÍTICO':
            return ['background-color: #ff9999; color: #333333'] * len(row)
        elif row['Estado Stock'] in ['MUY BAJO', 'BAJO']:
            return ['background-color: #fffd7d; color: #333333'] * len(row)
        else:
            return [''] * len(row)
    # Mostrar tabla con estilos
    st.dataframe(
        df_display.style.apply(highlight_stock, axis=1),
        use_container_width=True,
        height=400
    )
    
    # Botón de descarga
    st.download_button(
        label="📥 Descargar reporte en Excel",
        data=df_display.to_csv(index=False).encode('utf-8'),
        file_name=f'reporte_inventario_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )
    
    st.caption(f"Mostrando {len(df_filtrado):,} productos de {len(df):,} totales")

# ========================================
# TAB 2: ANÁLISIS DE VENTAS
# ========================================

with tab2:
    st.subheader("Análisis de Ventas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico: Ventas por tienda
        st.markdown("#### Ventas Totales por Tienda")
        ventas_por_tienda = df_filtrado.groupby('Tienda')[columna_ventas].sum().reset_index()
        ventas_por_tienda.columns = ['Tienda', 'Ventas']
        ventas_por_tienda = ventas_por_tienda.sort_values('Ventas', ascending=False)
        
        fig1 = px.bar(
            ventas_por_tienda,
            x='Tienda',
            y='Ventas',
            color='Ventas',
            color_continuous_scale='Blues',
            text='Ventas'
        )
        fig1.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig1.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="",
            yaxis_title="Unidades Vendidas"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Gráfico: Top 10 productos
        st.markdown("#### Top 10 Productos Más Vendidos")
        top_productos = df_filtrado.groupby('Producto')[columna_ventas].sum().reset_index()
        top_productos.columns = ['Producto', 'Ventas']
        top_productos = top_productos.sort_values('Ventas', ascending=False).head(10)
        
        fig2 = px.bar(
            top_productos,
            x='Ventas',
            y='Producto',
            orientation='h',
            color='Ventas',
            color_continuous_scale='Greens',
            text='Ventas'
        )
        fig2.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig2.update_layout(
            showlegend=False,
            height=400,
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Unidades Vendidas",
            yaxis_title=""
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Gráfico: Ventas por categoría
    st.markdown("#### Distribución de Ventas por Categoría")
    ventas_por_categoria = df_filtrado.groupby('Categoría')[columna_ventas].sum().reset_index()
    ventas_por_categoria.columns = ['Categoría', 'Ventas']
    
    fig3 = px.pie(
        ventas_por_categoria,
        values='Ventas',
        names='Categoría',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

# ========================================
# TAB 3: ROTACIÓN
# ========================================

with tab3:
    st.subheader("Análisis de Rotación de Mercancía")
    
    # Métricas de rotación
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rapida = len(df_filtrado[df_filtrado['Rotación'] == 'Rápida'])
        st.metric("🟢 Rotación Rápida", rapida)
    
    with col2:
        normal = len(df_filtrado[df_filtrado['Rotación'] == 'Normal'])
        st.metric("🟡 Rotación Normal", normal)
    
    with col3:
        lenta = len(df_filtrado[df_filtrado['Rotación'] == 'Lenta'])
        st.metric("🟠 Rotación Lenta", lenta)
    
    with col4:
        estancada = len(df_filtrado[df_filtrado['Rotación'] == 'Estancada'])
        st.metric("🔴 Estancada", estancada)
    
    st.markdown("---")
    
    # Gráfico: Stock vs Ventas
    st.markdown("#### Stock Actual vs Ventas")
    
    fig4 = go.Figure()
    
    # Agrupar por producto (promedio entre tiendas)
    df_agrupado = df_filtrado.groupby('Producto').agg({
        columna_ventas: 'sum',
        'Stock_Actual': 'sum',
        'Stock_Mínimo': 'mean',
        'Rotación': 'first'
    }).reset_index()
    
    df_agrupado = df_agrupado.sort_values(columna_ventas, ascending=False).head(15)
    
    # Colores según rotación
    colores = []
    for rotacion in df_agrupado['Rotación']:
        if rotacion == 'Rápida':
            colores.append('#28a745')
        elif rotacion == 'Normal':
            colores.append('#ffc107')
        elif rotacion == 'Lenta':
            colores.append('#fd7e14')
        else:
            colores.append('#dc3545')
    
    fig4.add_trace(go.Bar(
        name='Stock Actual',
        x=df_agrupado['Producto'],
        y=df_agrupado['Stock_Actual'],
        marker_color=colores
    ))
    
    fig4.add_trace(go.Scatter(
        name='Ventas',
        x=df_agrupado['Producto'],
        y=df_agrupado[columna_ventas],
        mode='lines+markers',
        marker=dict(size=8, color='red'),
        line=dict(width=2, color='red')
    ))
    
    fig4.update_layout(
        barmode='group',
        height=500,
        xaxis_tickangle=-45,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="",
        yaxis_title="Unidades"
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    
    # Tabla de productos estancados
    if estancada > 0:
        st.markdown("#### ⚠️ Productos Estancados (Rotación Lenta/Nula)")
        df_estancados = df_filtrado[df_filtrado['Rotación'].isin(['Estancada', 'Lenta'])][
            ['Tienda', 'Producto', 'Categoría', columna_ventas, 'Stock_Actual', 'Días_Cobertura', 'Rotación']
        ].copy()
        df_estancados = df_estancados.sort_values('Días_Cobertura', ascending=False)
        df_estancados.columns = ['Tienda', 'Producto', 'Categoría', f'Ventas ({periodo})', 'Stock', 'Días Cobertura', 'Estado']
        
        st.dataframe(df_estancados, use_container_width=True)

# ========================================
# FOOTER
# ========================================

st.markdown("---")
st.caption("💡 **Demo del Sistema de Inventario** - Los datos mostrados son ficticios para demostración")
st.caption("🔄 En producción, los datos se actualizarán automáticamente desde la base de datos del ERP")