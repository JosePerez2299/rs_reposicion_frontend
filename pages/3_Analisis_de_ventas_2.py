import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ============= CONFIGURACIÓN DE PÁGINA =============
st.set_page_config(
    page_title="Dashboard de Ventas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============= SIMULACIÓN DE RESPUESTA DEL BACKEND =============
def get_sales_data(filters):
    """
    Simula la respuesta de tu backend con fact_daily_sales
    """
    np.random.seed(42)
    
    fecha_inicio = datetime.strptime(filters["dates"]["fecha_inicio"], "%Y-%m-%d")
    fecha_fin = datetime.strptime(filters["dates"]["fecha_fin"], "%Y-%m-%d")
    
    productos = filters["products"] if filters["products"] else [
        "BOLSO EPONA - NAVY/PURPLE - UNICA",
        "BOLSO EPONA - BLACK/GOLD - UNICA",
        "CARTERA MINIMAL - BLACK - S",
        "CARTERA MINIMAL - BLACK - M",
        "MOCHILA URBAN - GREY - UNICA"
    ]
    
    tiendas = filters["stores"] if filters["stores"] else [101, 201, 301]
    
    data = []
    for producto in productos:
        for tienda in tiendas:
            dias = (fecha_fin - fecha_inicio).days + 1
            for i in range(dias):
                fecha = fecha_inicio + timedelta(days=i)
                
                if np.random.random() > 0.25:
                    multiplicador = np.random.uniform(0.7, 1.5)
                    ventas = int(np.random.randint(500, 4000) * multiplicador)
                    transacciones = int(np.random.randint(2, 30) * multiplicador)
                    
                    data.append({
                        "fecha": fecha.strftime("%Y-%m-%d"),
                        "producto": producto,
                        "tienda_id": tienda,
                        "tienda_nombre": f"Tienda {tienda}",
                        "ventas": ventas,
                        "transacciones": transacciones
                    })
    
    return pd.DataFrame(data)


def get_inventory_data(filters):
    """
    Simula la respuesta del backend con datos de inventario actual
    """
    np.random.seed(123)
    
    productos = filters["products"] if filters["products"] else [
        "BOLSO EPONA - NAVY/PURPLE - UNICA",
        "BOLSO EPONA - BLACK/GOLD - UNICA",
        "CARTERA MINIMAL - BLACK - S",
        "CARTERA MINIMAL - BLACK - M",
        "MOCHILA URBAN - GREY - UNICA"
    ]
    
    tiendas = filters["stores"] if filters["stores"] else [101, 201, 301]
    
    data = []
    for producto in productos:
        for tienda in tiendas:
            # Stock actual (algunas tiendas con bajo stock)
            stock_actual = np.random.randint(0, 50)
            
            # Stock mínimo recomendado (varía por producto)
            stock_minimo = np.random.randint(10, 20)
            
            # Stock máximo (capacidad de almacenamiento)
            stock_maximo = np.random.randint(40, 80)
            
            # Costo unitario
            costo_unitario = np.random.randint(50, 200)
            
            data.append({
                "producto": producto,
                "tienda_id": tienda,
                "tienda_nombre": f"Tienda {tienda}",
                "stock_actual": stock_actual,
                "stock_minimo": stock_minimo,
                "stock_maximo": stock_maximo,
                "costo_unitario": costo_unitario,
                "valor_inventario": stock_actual * costo_unitario
            })
    
    return pd.DataFrame(data)


# ============= FUNCIONES DE ANÁLISIS DE ROTACIÓN =============
def calcular_rotacion(df_ventas, df_inventario, dias_periodo):
    """
    Calcula métricas de rotación de inventario
    """
    # Unidades vendidas por producto y tienda
    df_unidades = df_ventas.groupby(['producto', 'tienda_nombre'])['transacciones'].sum().reset_index()
    df_unidades.rename(columns={'transacciones': 'unidades_vendidas'}, inplace=True)
    
    # Merge con inventario
    df_rotacion = df_inventario.merge(
        df_unidades,
        on=['producto', 'tienda_nombre'],
        how='left'
    )
    
    df_rotacion['unidades_vendidas'] = df_rotacion['unidades_vendidas'].fillna(0)
    
    # Calcular métricas
    df_rotacion['venta_diaria_promedio'] = (df_rotacion['unidades_vendidas'] / dias_periodo).round(2)
    
    # Días de inventario = stock_actual / venta_diaria_promedio
    df_rotacion['dias_inventario'] = df_rotacion.apply(
        lambda row: round(row['stock_actual'] / row['venta_diaria_promedio'], 1) 
        if row['venta_diaria_promedio'] > 0 else 999,
        axis=1
    )
    
    # Rotación (veces que se vende el inventario en el periodo)
    df_rotacion['indice_rotacion'] = df_rotacion.apply(
        lambda row: round(row['unidades_vendidas'] / row['stock_actual'], 2) 
        if row['stock_actual'] > 0 else 0,
        axis=1
    )
    
    # Nivel de stock
    def clasificar_stock(row):
        if row['stock_actual'] == 0:
            return "SIN STOCK"
        elif row['stock_actual'] < row['stock_minimo']:
            return "CRÍTICO"
        elif row['stock_actual'] >= row['stock_maximo']:
            return "EXCESO"
        else:
            return "NORMAL"
    
    df_rotacion['nivel_stock'] = df_rotacion.apply(clasificar_stock, axis=1)
    
    # Cantidad a reponer
    df_rotacion['cantidad_reponer'] = df_rotacion.apply(
        lambda row: max(0, row['stock_maximo'] - row['stock_actual']) 
        if row['nivel_stock'] in ['SIN STOCK', 'CRÍTICO'] else 0,
        axis=1
    )
    
    df_rotacion['costo_reposicion'] = df_rotacion['cantidad_reponer'] * df_rotacion['costo_unitario']
    
    return df_rotacion


# ============= CARGAR DATOS UNA SOLA VEZ =============
@st.cache_data
def load_data(filtros):
    return get_sales_data(filtros)

@st.cache_data
def load_inventory(filtros):
    return get_inventory_data(filtros)


# ============= FILTROS =============
filtros = {
    "dates": {"fecha_inicio": "2026-02-01", "fecha_fin": "2026-02-10"},
    "stores": [101, 201, 301],
    "products": [
        "BOLSO EPONA - NAVY/PURPLE - UNICA",
        "BOLSO EPONA - BLACK/GOLD - UNICA",
        "CARTERA MINIMAL - BLACK - S",
        "CARTERA MINIMAL - BLACK - M",
        "MOCHILA URBAN - GREY - UNICA"
    ],
    "categories": []
}

# Cargar datos
with st.spinner("Cargando datos..."):
    df_raw = load_data(filtros)
    df_inventory = load_inventory(filtros)

if df_raw.empty:
    st.warning("No se encontraron datos para los filtros seleccionados")
    st.stop()

# Calcular días del periodo
fecha_inicio = datetime.strptime(filtros["dates"]["fecha_inicio"], "%Y-%m-%d")
fecha_fin = datetime.strptime(filtros["dates"]["fecha_fin"], "%Y-%m-%d")
dias_periodo = (fecha_fin - fecha_inicio).days + 1

# Calcular rotación
df_rotacion = calcular_rotacion(df_raw, df_inventory, dias_periodo)

# Calcular métricas globales
total_ventas = df_raw['ventas'].sum()
total_transacciones = df_raw['transacciones'].sum()
ticket_promedio = total_ventas / total_transacciones if total_transacciones > 0 else 0


# ============= NAVEGACIÓN =============
st.title("📊 Dashboard de Ventas e Inventario")

# Crear tabs para navegación
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Resumen General",
    "🔍 Análisis Detallado",
    "📊 Comparativas",
    "📦 Inventario y Rotación",
    "💾 Datos Crudos"
])


# ============= TAB 1: RESUMEN GENERAL =============
with tab1:
    st.header("Resumen General")
    
    # Mostrar filtros activos
    with st.expander("🔍 Filtros aplicados", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**📅 Periodo:** {filtros['dates']['fecha_inicio']} al {filtros['dates']['fecha_fin']}")
            st.write(f"**🏪 Tiendas:** {len(filtros['stores'])} seleccionadas")
        with col2:
            st.write(f"**📦 Productos:** {len(filtros['products'])} seleccionados")
    
    st.divider()
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Ventas Totales", f"${total_ventas:,.0f}")
    with col2:
        st.metric("Transacciones", f"{total_transacciones:,}")
    with col3:
        st.metric("Ticket Promedio", f"${ticket_promedio:,.2f}")
    with col4:
        st.metric("Productos", len(filtros['products']))
    with col5:
        st.metric("Tiendas", len(filtros['stores']))
    
    st.divider()
    
    # Ranking de productos
    st.subheader("🏆 Ranking de Productos")
    
    df_productos = df_raw.groupby("producto").agg({
        "ventas": "sum",
        "transacciones": "sum"
    }).reset_index()
    
    df_productos['ticket_promedio'] = (df_productos['ventas'] / df_productos['transacciones']).round(2)
    df_productos['porcentaje'] = (df_productos['ventas'] / total_ventas * 100).round(1)
    df_productos = df_productos.sort_values("ventas", ascending=False)
    df_productos['ranking'] = range(1, len(df_productos) + 1)
    df_productos = df_productos[['ranking', 'producto', 'ventas', 'transacciones', 'ticket_promedio', 'porcentaje']]
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.dataframe(
            df_productos.style.format({
                "ventas": "${:,.0f}",
                "transacciones": "{:,}",
                "ticket_promedio": "${:,.2f}",
                "porcentaje": "{:.1f}%"
            }).background_gradient(subset=['ventas'], cmap='YlGn'),
            use_container_width=True,
            hide_index=True,
            height=400
        )
    
    with col2:
        st.write("**Distribución de Ventas**")
        fig_pie = px.pie(
            df_productos, 
            values='ventas', 
            names='producto',
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    
    # Análisis por tienda
    st.subheader("🏪 Resumen por Tienda")
    
    df_tiendas = df_raw.groupby("tienda_nombre").agg({
        "ventas": "sum",
        "transacciones": "sum"
    }).reset_index()
    
    df_tiendas['ticket_promedio'] = (df_tiendas['ventas'] / df_tiendas['transacciones']).round(2)
    df_tiendas['porcentaje'] = (df_tiendas['ventas'] / total_ventas * 100).round(1)
    df_tiendas = df_tiendas.sort_values("ventas", ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(
            df_tiendas.style.format({
                "ventas": "${:,.0f}",
                "transacciones": "{:,}",
                "ticket_promedio": "${:,.2f}",
                "porcentaje": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        fig_bar = px.bar(
            df_tiendas,
            x='tienda_nombre',
            y='ventas',
            text='ventas',
            title='Ventas por Tienda'
        )
        fig_bar.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.divider()
    
    # Evolución temporal general
    st.subheader("📈 Evolución Temporal")
    
    df_temporal_general = df_raw.groupby("fecha").agg({
        "ventas": "sum",
        "transacciones": "sum"
    }).reset_index()
    
    fig_evol = go.Figure()
    fig_evol.add_trace(go.Scatter(
        x=df_temporal_general['fecha'],
        y=df_temporal_general['ventas'],
        mode='lines+markers',
        name='Ventas',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8),
        fill='tozeroy'
    ))
    
    fig_evol.update_layout(
        title='Evolución Diaria de Ventas',
        xaxis_title='Fecha',
        yaxis_title='Ventas ($)',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_evol, use_container_width=True)

# ============= TAB 2: ANÁLISIS DETALLADO =============
with tab2:
    st.header("Análisis Detallado por Producto")
    
    productos_ordenados = df_productos['producto'].tolist()
    
    for idx, producto in enumerate(productos_ordenados, 1):
        df_producto = df_raw[df_raw['producto'] == producto]
        
        ventas_producto = df_producto['ventas'].sum()
        transacciones_producto = df_producto['transacciones'].sum()
        ticket_prom = ventas_producto / transacciones_producto if transacciones_producto > 0 else 0
        
        # Calcular tendencia
        df_temporal_prod = df_producto.groupby('fecha')['ventas'].sum().reset_index()
        if len(df_temporal_prod) > 1:
            mid_point = len(df_temporal_prod) // 2
            ventas_primera = df_temporal_prod.iloc[:mid_point]['ventas'].sum()
            ventas_segunda = df_temporal_prod.iloc[mid_point:]['ventas'].sum()
            tendencia = ((ventas_segunda - ventas_primera) / ventas_primera * 100) if ventas_primera > 0 else 0
            tendencia_emoji = "📈" if tendencia > 5 else "📉" if tendencia < -5 else "➡️"
        else:
            tendencia = 0
            tendencia_emoji = "➡️"
        
        with st.expander(
            f"**#{idx} - {producto}** | ${ventas_producto:,.0f} | {transacciones_producto:,} trans. | Ticket: ${ticket_prom:,.2f} {tendencia_emoji}",
            expanded=(idx == 1)
        ):
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Ventas", f"${ventas_producto:,.0f}")
            with col2:
                st.metric("Transacciones", f"{transacciones_producto:,}")
            with col3:
                st.metric("Ticket Promedio", f"${ticket_prom:,.2f}")
            with col4:
                porcentaje_prod = (ventas_producto / total_ventas * 100)
                st.metric("% del Total", f"{porcentaje_prod:.1f}%")
            
            # Sub-tabs
            subtab1, subtab2, subtab3 = st.tabs(["🏪 Por Tienda", "📅 Evolución", "📊 Stats"])
            
            with subtab1:
                # Obtener datos de inventario y rotación para este producto
                df_rotacion_prod = df_rotacion[df_rotacion['producto'] == producto].copy()
                
                # Agregar datos de ventas por tienda
                df_tiendas_prod = df_producto.groupby(["tienda_id", "tienda_nombre"]).agg({
                    "transacciones": "sum",
                    "ventas": "sum"
                }).reset_index()
                
                # Merge con datos de rotación/inventario
                df_tabla_base = df_rotacion_prod.merge(
                    df_tiendas_prod,
                    on=["tienda_nombre"],
                    how="left"
                )
                
                # EXPANDIR CADA FILA EN 3 VARIANTES (SIZES)
                filas_expandidas = []
                
                for _, row in df_tabla_base.iterrows():
                    # Extraer número de tienda
                    tienda_nombre = row['tienda_nombre']
                    tienda_num = int(tienda_nombre.split()[-1]) if tienda_nombre.split()[-1].isdigit() else 0
                    
                    # Crear 3 variantes por cada tienda
                    for variante in range(3):
                        # Generar código único: PRODUCTO-TIENDA-VARIANTE
                        codigo = f"{idx:03d}{tienda_num % 100:02d}{variante}"
                        
                        # Distribuir las métricas entre las 3 variantes (simulado)
                        # En producción, estos datos vendrían directamente de la BD
                        np.random.seed(int(codigo))  # Para resultados consistentes
                        
                        # Distribuir stock (la suma de las 3 variantes = stock total)
                        pesos = np.random.dirichlet(np.ones(3))
                        stock_variante = int(row['stock_actual'] * pesos[variante])
                        
                        # Distribuir ventas en unidades
                        ventas_variante = int(row['transacciones'] * pesos[variante])
                        
                        # Distribuir ventas en dinero
                        ventas_dinero_variante = int(row['ventas'] * pesos[variante])
                        
                        # Distribuir compras (unidades_vendidas)
                        compras_variante = int(row['unidades_vendidas'] * pesos[variante])
                        
                        # Rotación se mantiene similar (pequeña variación)
                        rotacion_variante = row['indice_rotacion'] * np.random.uniform(0.8, 1.2)
                        
                        filas_expandidas.append({
                            'Código Producto': codigo,
                            'Tienda': tienda_nombre,
                            'Nombre Producto': row['producto'],
                            'Compras': compras_variante,
                            'Ventas': ventas_variante,
                            'Ventas $': ventas_dinero_variante,
                            'Stock': stock_variante,
                            'Porcentaje Rotación': rotacion_variante
                        })
                
                # Crear DataFrame expandido con índice nuevo
                df_tabla_detallada = pd.DataFrame(filas_expandidas)
                df_tabla_detallada = df_tabla_detallada.reset_index(drop=True)
                
                # Ordenar por tienda y código
                df_tabla_detallada = df_tabla_detallada.sort_values(['Tienda', 'Código Producto'], ascending=[True, True])
                df_tabla_detallada = df_tabla_detallada.reset_index(drop=True)
      # ================= FILTROS TABLA DETALLADA =================
                st.markdown("### Filtros")

                colf1, colf2 = st.columns(2)

                with colf1:
                    tiendas_disponibles = sorted(df_tabla_detallada["Tienda"].unique())
                    tiendas_seleccionadas = st.multiselect(
                        "Filtrar por Tienda",
                        options=tiendas_disponibles,
                        default=tiendas_disponibles,
                        key=f"tiendas_filter_{idx}_{producto}"  # Key única por producto
                    )

                with colf2:
                    codigo_busqueda = st.text_input(
                        "Filtrar por Código",
                        placeholder="Ej: 001010",
                        key=f"codigo_filter_{idx}_{producto}"  # Key única por producto
                    )

                # Aplicar filtros
                df_filtrado = df_tabla_detallada.copy()

                if tiendas_seleccionadas:
                    df_filtrado = df_filtrado[
                        df_filtrado["Tienda"].isin(tiendas_seleccionadas)
                    ]

                if codigo_busqueda:
                    df_filtrado = df_filtrado[
                        df_filtrado["Código Producto"]
                        .astype(str)
                        .str.contains(codigo_busqueda.strip(), case=False, na=False)
                    ]

                # Reordenar luego del filtro
                df_filtrado = df_filtrado.sort_values(
                    ['Tienda', 'Código Producto'],
                    ascending=[True, True]
                ).reset_index(drop=True)

                # Mostrar tabla CON EL DATAFRAME FILTRADO
                st.dataframe(
                    df_filtrado.style.format({  # CAMBIAR df_tabla_detallada por df_filtrado
                        "Compras": "{:,}",
                        "Ventas": "{:,}",
                        "Ventas $": "${:,.0f}",
                        "Stock": "{:,}",
                        "Porcentaje Rotación": "{:.2f}"
                    }).background_gradient(subset=['Ventas $'], cmap='YlGn'),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'Código Producto': st.column_config.TextColumn(
                            'Código Producto',
                            width='small'
                        ),
                        'Tienda': st.column_config.TextColumn(
                            'Tienda',
                            width='small'
                        ),
                        'Nombre Producto': st.column_config.TextColumn(
                            'Nombre Producto',
                            width='large'
                        ),
                        'Compras': st.column_config.NumberColumn(
                            'Compras',
                            help='Unidades compradas/recibidas',
                            format='%d'
                        ),
                        'Ventas': st.column_config.NumberColumn(
                            'Ventas',
                            help='Unidades vendidas',
                            format='%d'
                        ),
                        'Ventas $': st.column_config.NumberColumn(
                            'Ventas $',
                            help='Monto en dinero',
                            format='$%d'
                        ),
                        'Stock': st.column_config.NumberColumn(
                            'Stock',
                            format='%d'
                        ),
                        'Porcentaje Rotación': st.column_config.NumberColumn(
                            '% Rotación',
                            format='%.2f'
                        )
                    }
                )

 

# ============= TAB 3: COMPARATIVAS =============
with tab3:
    st.header("Análisis Comparativo")
    
    # Matriz productos x tiendas
    st.subheader("📊 Matriz: Productos x Tiendas")
    
    df_matriz = df_raw.pivot_table(
        index='producto',
        columns='tienda_nombre',
        values='ventas',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    df_matriz['TOTAL'] = df_matriz.iloc[:, 1:].sum(axis=1)
    df_matriz = df_matriz.sort_values('TOTAL', ascending=False)
    
    st.dataframe(
        df_matriz.style.format(
            {col: "${:,.0f}" for col in df_matriz.columns if col != 'producto'}
        ).background_gradient(subset=[col for col in df_matriz.columns if col != 'producto'], cmap='YlGnBu'),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # Heatmap
    st.subheader("🔥 Mapa de Calor")
    
    df_heatmap = df_raw.pivot_table(
        index='producto',
        columns='tienda_nombre',
        values='ventas',
        aggfunc='sum',
        fill_value=0
    )
    
    fig_heatmap = px.imshow(
        df_heatmap,
        labels=dict(x="Tienda", y="Producto", color="Ventas"),
        x=df_heatmap.columns,
        y=df_heatmap.index,
        color_continuous_scale='YlGnBu',
        aspect="auto"
    )
    fig_heatmap.update_layout(height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.divider()
    
    # Evolución comparativa
    st.subheader("📈 Evolución Temporal Comparativa")
    
    df_temporal_all = df_raw.groupby(['fecha', 'producto'])['ventas'].sum().reset_index()
    
    fig_comp = px.line(
        df_temporal_all,
        x='fecha',
        y='ventas',
        color='producto',
        markers=True,
        title='Comparación de Ventas por Producto'
    )
    fig_comp.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig_comp, use_container_width=True)
    
    st.divider()
    
    # Comparación de tiendas
    st.subheader("🏪 Ventas por Tienda y Producto")
    
    df_tienda_producto = df_raw.groupby(['tienda_nombre', 'producto'])['ventas'].sum().reset_index()
    
    fig_grouped = px.bar(
        df_tienda_producto,
        x='tienda_nombre',
        y='ventas',
        color='producto',
        barmode='group',
        title='Ventas por Tienda y Producto',
        text='ventas'
    )
    fig_grouped.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig_grouped.update_layout(height=500)
    st.plotly_chart(fig_grouped, use_container_width=True)


# ============= TAB 4: INVENTARIO Y ROTACIÓN =============
with tab4:
    st.write("INVENTARIO Y ROTACIÓN")
    st.header("📦 Gestión de Inventario y Rotación")
    
    # Métricas globales de inventario
    st.subheader("📊 Resumen de Inventario")
    
    total_stock = df_inventory['stock_actual'].sum()
    valor_total_inventario = df_inventory['valor_inventario'].sum()
    productos_sin_stock = len(df_rotacion[df_rotacion['nivel_stock'] == 'SIN STOCK'])
    productos_criticos = len(df_rotacion[df_rotacion['nivel_stock'] == 'CRÍTICO'])
    productos_exceso = len(df_rotacion[df_rotacion['nivel_stock'] == 'EXCESO'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Stock Total", f"{total_stock:,} unidades")
    with col2:
        st.metric("Valor Inventario", f"${valor_total_inventario:,.0f}")
    with col3:
        st.metric("Sin Stock", productos_sin_stock, delta=f"-{productos_sin_stock}", delta_color="inverse")
    with col4:
        st.metric("Stock Crítico", productos_criticos, delta=f"-{productos_criticos}", delta_color="inverse")
    with col5:
        st.metric("Exceso", productos_exceso, delta=f"+{productos_exceso}", delta_color="inverse")
    
    st.divider()
    
    # Alertas de reposición
    st.subheader("🚨 Alertas de Reposición")
    
    df_alertas = df_rotacion[df_rotacion['nivel_stock'].isin(['SIN STOCK', 'CRÍTICO'])].copy()
    df_alertas = df_alertas.sort_values('stock_actual')
    
    if len(df_alertas) > 0:
        st.error(f"⚠️ {len(df_alertas)} productos requieren reposición urgente")
        
        st.dataframe(
            df_alertas[[
                'producto', 'tienda_nombre', 'stock_actual', 'stock_minimo', 
                'venta_diaria_promedio', 'dias_inventario', 'cantidad_reponer', 'costo_reposicion'
            ]].style.format({
                'stock_actual': '{:,}',
                'stock_minimo': '{:,}',
                'venta_diaria_promedio': '{:.2f}',
                'dias_inventario': '{:.1f}',
                'cantidad_reponer': '{:,}',
                'costo_reposicion': '${:,.0f}'
            }).apply(
                lambda x: ['background-color: #ffcccc' if v == 'SIN STOCK' 
                          else 'background-color: #ffe6cc' for v in df_alertas['nivel_stock']],
                axis=0
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                'producto': 'Producto',
                'tienda_nombre': 'Tienda',
                'stock_actual': 'Stock Actual',
                'stock_minimo': 'Stock Mínimo',
                'venta_diaria_promedio': 'Venta Diaria',
                'dias_inventario': 'Días de Stock',
                'cantidad_reponer': 'Cantidad a Reponer',
                'costo_reposicion': 'Costo Reposición'
            }
        )
        
        # Resumen de reposición
        total_reposicion = df_alertas['cantidad_reponer'].sum()
        costo_total_reposicion = df_alertas['costo_reposicion'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📦 **Total unidades a reponer:** {total_reposicion:,}")
        with col2:
            st.info(f"💰 **Costo total de reposición:** ${costo_total_reposicion:,.0f}")
        
        # Botón de descarga de orden de compra
        csv_reposicion = df_alertas[[
            'producto', 'tienda_nombre', 'stock_actual', 'cantidad_reponer', 'costo_unitario', 'costo_reposicion'
        ]].to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Descargar Orden de Compra",
            data=csv_reposicion,
            file_name=f"orden_compra_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.success("✅ No hay productos que requieran reposición urgente")
    
    st.divider()
    
    # Análisis de rotación
    st.subheader("🔄 Análisis de Rotación de Inventario")
    
    # Filtrar por nivel de stock
    col1, col2 = st.columns([1, 3])
    
    with col1:
        nivel_filtro = st.multiselect(
            "Filtrar por nivel",
            options=['NORMAL', 'CRÍTICO', 'SIN STOCK', 'EXCESO'],
            default=['NORMAL', 'CRÍTICO', 'SIN STOCK', 'EXCESO']
        )
    
    df_rotacion_filtrado = df_rotacion[df_rotacion['nivel_stock'].isin(nivel_filtro)]
    
    # Tabla de rotación
    st.dataframe(
        df_rotacion_filtrado[[
            'producto', 'tienda_nombre', 'stock_actual', 'unidades_vendidas',
            'venta_diaria_promedio', 'dias_inventario', 'indice_rotacion', 'nivel_stock'
        ]].style.format({
            'stock_actual': '{:,}',
            'unidades_vendidas': '{:,}',
            'venta_diaria_promedio': '{:.2f}',
            'dias_inventario': '{:.1f}',
            'indice_rotacion': '{:.2f}'
        }).applymap(
            lambda x: 'background-color: #ffcccc' if x == 'SIN STOCK'
            else 'background-color: #ffe6cc' if x == 'CRÍTICO'
            else 'background-color: #fff4cc' if x == 'EXCESO'
            else '',
            subset=['nivel_stock']
        ),
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            'producto': 'Producto',
            'tienda_nombre': 'Tienda',
            'stock_actual': 'Stock',
            'unidades_vendidas': f'Ventas ({dias_periodo}d)',
            'venta_diaria_promedio': 'Venta/Día',
            'dias_inventario': 'Días Stock',
            'indice_rotacion': 'Rotación',
            'nivel_stock': 'Estado'
        }
    )
    
    st.divider()
    
    # Visualizaciones de rotación
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Días de Inventario por Producto**")
        df_dias_inv = df_rotacion.groupby('producto')['dias_inventario'].mean().reset_index()
        df_dias_inv = df_dias_inv[df_dias_inv['dias_inventario'] < 999]  # Excluir productos sin ventas
        df_dias_inv = df_dias_inv.sort_values('dias_inventario')
        
        fig_dias = px.bar(
            df_dias_inv,
            x='dias_inventario',
            y='producto',
            orientation='h',
            text='dias_inventario',
            color='dias_inventario',
            color_continuous_scale=['green', 'yellow', 'red']
        )
        fig_dias.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_dias.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_dias, use_container_width=True)
    
    with col2:
        st.write("**Índice de Rotación por Producto**")
        df_rot_prod = df_rotacion.groupby('producto')['indice_rotacion'].mean().reset_index()
        df_rot_prod = df_rot_prod.sort_values('indice_rotacion', ascending=False)
        
        fig_rot = px.bar(
            df_rot_prod,
            x='indice_rotacion',
            y='producto',
            orientation='h',
            text='indice_rotacion',
            color='indice_rotacion',
            color_continuous_scale='Blues'
        )
        fig_rot.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_rot.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_rot, use_container_width=True)
    
    st.divider()
    
    # Distribución de nivel de stock
    st.subheader("📈 Distribución de Niveles de Stock")
    
    df_nivel_dist = df_rotacion['nivel_stock'].value_counts().reset_index()
    df_nivel_dist.columns = ['nivel', 'cantidad']
    
    fig_nivel = px.pie(
        df_nivel_dist,
        values='cantidad',
        names='nivel',
        title='Distribución por Nivel de Stock',
        color='nivel',
        color_discrete_map={
            'NORMAL': '#90EE90',
            'CRÍTICO': '#FFD700',
            'SIN STOCK': '#FF6B6B',
            'EXCESO': '#87CEEB'
        }
    )
    fig_nivel.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_nivel, use_container_width=True)
    
    st.divider()
    
    # Análisis detallado por producto
    st.subheader("🔍 Análisis Detallado de Rotación")
    
    producto_seleccionado = st.selectbox(
        "Seleccionar producto para análisis detallado",
        options=df_rotacion['producto'].unique()
    )
    
    df_prod_detalle = df_rotacion[df_rotacion['producto'] == producto_seleccionado]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Stock Total", f"{df_prod_detalle['stock_actual'].sum():,}")
    with col2:
        st.metric("Ventas (periodo)", f"{df_prod_detalle['unidades_vendidas'].sum():,.0f}")
    with col3:
        st.metric("Rotación Promedio", f"{df_prod_detalle['indice_rotacion'].mean():.2f}")
    with col4:
        st.metric("Días Inventario", f"{df_prod_detalle['dias_inventario'].mean():.1f}")
    
    st.dataframe(
        df_prod_detalle[[
            'tienda_nombre', 'stock_actual', 'stock_minimo', 'stock_maximo',
            'unidades_vendidas', 'venta_diaria_promedio', 'dias_inventario',
            'indice_rotacion', 'nivel_stock', 'cantidad_reponer'
        ]].style.format({
            'stock_actual': '{:,}',
            'stock_minimo': '{:,}',
            'stock_maximo': '{:,}',
            'unidades_vendidas': '{:,}',
            'venta_diaria_promedio': '{:.2f}',
            'dias_inventario': '{:.1f}',
            'indice_rotacion': '{:.2f}',
            'cantidad_reponer': '{:,}'
        }),
        use_container_width=True,
        hide_index=True
    )


# ============= TAB 5: DATOS CRUDOS =============
with tab5:
    st.header("Datos Crudos")
    
    st.info("💡 Aquí puedes explorar y exportar los datos completos")
    
    # Selector de dataset
    dataset_seleccionado = st.radio(
        "Seleccionar dataset",
        options=["Ventas", "Inventario", "Rotación"],
        horizontal=True
    )
    
    # if dataset_seleccionado == "Ventas":
    #     df_mostrar = df_raw
    # elif dataset_seleccionado == "Inventario":
    #     df_mostrar = df_inventory
    # else:
    #     df_mostrar = df_rotacion
    
    # # Filtros adicionales para los datos
    # col1, col2, col3 = st.columns(3)
    
    # with col1:
    #     productos_filter = st.multiselect(
    #         "Filtrar por producto",
    #         options=df_mostrar['producto'].unique().tolist(),
    #         default=df_mostrar['producto'].unique().tolist(),
    #         key="filter_productos"
    #     )
    
    # with col2:
    #     tiendas_filter = st.multiselect(
    #         "Filtrar por tienda",
    #         options=df_mostrar['tienda_nombre'].unique().tolist(),
    #         default=df_mostrar['tienda_nombre'].unique().tolist(),
    #         key="filter_tiendas"
    #     )
    
    # if dataset_seleccionado == "Ventas":
    #     with col3:
    #         fecha_filter = st.date_input(
    #             "Filtrar por fecha",
    #             value=(
    #                 datetime.strptime(filtros['dates']['fecha_inicio'], "%Y-%m-%d"),
    #                 datetime.strptime(filtros['dates']['fecha_fin'], "%Y-%m-%d")
    #             ),
    #             format="YYYY-MM-DD",
    #             key="filter_fecha"
    #         )
    
    # # Aplicar filtros
    # df_filtrado = df_mostrar.copy()
    
    # if productos_filter:
    #     df_filtrado = df_filtrado[df_filtrado['producto'].isin(productos_filter)]
    
    # if tiendas_filter:
    #     df_filtrado = df_filtrado[df_filtrado['tienda_nombre'].isin(tiendas_filter)]
    
    # if dataset_seleccionado == "Ventas" and len(fecha_filter) == 2:
    #     fecha_inicio_filter = fecha_filter[0].strftime("%Y-%m-%d")
    #     fecha_fin_filter = fecha_filter[1].strftime("%Y-%m-%d")
    #     df_filtrado = df_filtrado[
    #         (df_filtrado['fecha'] >= fecha_inicio_filter) & 
    #         (df_filtrado['fecha'] <= fecha_fin_filter)
    #     ]
    
    # st.divider()
    
    # # Mostrar estadísticas del dataset filtrado
    # col1, col2, col3, col4 = st.columns(4)
    # with col1:
    #     st.metric("Total Registros", f"{len(df_filtrado):,}")
    # with col2:
    #     if dataset_seleccionado == "Ventas":
    #         st.metric("Ventas", f"${df_filtrado['ventas'].sum():,.0f}")
    #     elif dataset_seleccionado == "Inventario":
    #         st.metric("Stock Total", f"{df_filtrado['stock_actual'].sum():,}")
    #     else:
    #         st.metric("Stock Total", f"{df_filtrado['stock_actual'].sum():,}")
    # with col3:
    #     if dataset_seleccionado == "Ventas":
    #         st.metric("Transacciones", f"{df_filtrado['transacciones'].sum():,}")
    #     elif dataset_seleccionado == "Inventario":
    #         st.metric("Valor Inventario", f"${df_filtrado['valor_inventario'].sum():,.0f}")
    #     else:
    #         st.metric("Unidades Vendidas", f"{df_filtrado['unidades_vendidas'].sum():,.0f}")
    # with col4:
    #     st.metric("Productos Únicos", len(df_filtrado['producto'].unique()))
    
    # st.divider()
    
    # # Mostrar datos
    # st.dataframe(
    #     df_filtrado,
    #     use_container_width=True,
    #     height=600
    # )
    
    # st.divider()
    
    # # Opciones de descarga
    # col1, col2, col3 = st.columns(3)
    
    # with col1:
    #     csv = df_filtrado.to_csv(index=False).encode('utf-8')
    #     st.download_button(
    #         label=f"📥 Descargar {dataset_seleccionado}",
    #         data=csv,
    #         file_name=f"{dataset_seleccionado.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    #         mime="text/csv",
    #     )
    
    # with col2:
    #     st.write(f"**Dataset:** {dataset_seleccionado}")
    #     st.write(f"**Registros:** {len(df_filtrado):,}")
    
    # with col3:
    #     st.write("**Formato:** CSV (UTF-8)")
    #     st.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")