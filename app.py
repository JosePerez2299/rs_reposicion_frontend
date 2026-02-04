import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Reporte de Inventario", layout="wide")

# Generar datos dummy
np.random.seed(42)

tiendas = ['Barquisimeto', 'Candelaria', 'Cerro Verde', 'Chacao', 'Maracaibo', 'Megacenter', 'Online']
modelos = ['016501']
colores = ['BLACK/DK.GREY', 'BROWN/BLACK', 'DK.GREY/LT.GREY', 'WHITE/BROWN']

# Crear dataset
data_rows = []
for tienda in tiendas:
    for modelo in modelos:
        for color in colores:
            compra = np.random.randint(10, 50)
            ventas = np.random.randint(1, 30)
            existencia = np.random.randint(0, 40)
            rotacion = round((ventas / compra * 100) if compra > 0 else 0)
            
            data_rows.append({
                'Tienda': tienda,
                'Modelo': modelo,
                'Descripción': f'CRIME MEN - {color}',
                'Compra': compra,
                'Ventas': ventas,
                'Existencia': existencia,
                'Rotación': f'{rotacion}%'
            })

df = pd.DataFrame(data_rows)

# Título
st.title("📊 Reporte de Inventario - ERP")
st.markdown("---")

# Sidebar para filtros
st.sidebar.header("🔍 Filtros")

# Filtro por tienda
tiendas_seleccionadas = st.sidebar.multiselect(
    "Seleccionar Tiendas:",
    options=['Todas'] + tiendas,
    default=['Todas']
)

# Filtro por modelo
modelos_disponibles = df['Modelo'].unique().tolist()
modelos_seleccionados = st.sidebar.multiselect(
    "Seleccionar Modelos:",
    options=['Todos'] + modelos_disponibles,
    default=['Todos']
)

# Filtro por descripción/color
colores_disponibles = df['Descripción'].unique().tolist()
colores_seleccionados = st.sidebar.multiselect(
    "Seleccionar Colores:",
    options=['Todos'] + colores_disponibles,
    default=['Todos']
)

# Aplicar filtros
df_filtrado = df.copy()

if 'Todas' not in tiendas_seleccionadas and tiendas_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado['Tienda'].isin(tiendas_seleccionadas)]

if 'Todos' not in modelos_seleccionados and modelos_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['Modelo'].isin(modelos_seleccionados)]

if 'Todos' not in colores_seleccionados and colores_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['Descripción'].isin(colores_seleccionados)]

# Métricas generales
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Resumen General")

# Convertir rotación a numérico para cálculos
df_filtrado['Rotación_num'] = df_filtrado['Rotación'].str.rstrip('%').astype(int)

total_compra = df_filtrado['Compra'].sum()
total_ventas = df_filtrado['Ventas'].sum()
total_existencia = df_filtrado['Existencia'].sum()
rotacion_promedio = round(df_filtrado['Rotación_num'].mean())

st.sidebar.metric("Total Compra", total_compra)
st.sidebar.metric("Total Ventas", total_ventas)
st.sidebar.metric("Total Existencia", total_existencia)
st.sidebar.metric("Rotación Promedio", f"{rotacion_promedio}%")

# Métricas en la parte superior
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🛒 Compra Total", total_compra)
with col2:
    st.metric("💰 Ventas Totales", total_ventas)
with col3:
    st.metric("📦 Existencia Total", total_existencia)
with col4:
    st.metric("🔄 Rotación Promedio", f"{rotacion_promedio}%")

st.markdown("---")

# Función para crear tabla agrupada con totales
def crear_tabla_con_totales(df_filtrado):
    # Agrupar por tienda
    resultados = []
    
    for tienda in df_filtrado['Tienda'].unique():
        df_tienda = df_filtrado[df_filtrado['Tienda'] == tienda]
        
        # Agregar fila de tienda (encabezado)
        resultados.append({
            'Tienda': f'▼ {tienda}',
            'Modelo': '',
            'Descripción': '',
            'Compra': '',
            'Ventas': '',
            'Existencia': '',
            'Rotación': ''
        })
        
        # Agregar filas de productos
        for _, row in df_tienda.iterrows():
            resultados.append({
                'Tienda': '',
                'Modelo': row['Modelo'],
                'Descripción': row['Descripción'],
                'Compra': row['Compra'],
                'Ventas': row['Ventas'],
                'Existencia': row['Existencia'],
                'Rotación': row['Rotación']
            })
        
        # Fila de total por modelo
        total_compra = df_tienda['Compra'].sum()
        total_ventas = df_tienda['Ventas'].sum()
        total_existencia = df_tienda['Existencia'].sum()
        rotacion_tienda = round((total_ventas / total_compra * 100) if total_compra > 0 else 0)
        
        resultados.append({
            'Tienda': '',
            'Modelo': f'Total {df_tienda["Modelo"].iloc[0]}',
            'Descripción': '',
            'Compra': total_compra,
            'Ventas': total_ventas,
            'Existencia': total_existencia,
            'Rotación': f'{rotacion_tienda}%'
        })
        
        # Fila de total por tienda
        resultados.append({
            'Tienda': f'Total {tienda}',
            'Modelo': '',
            'Descripción': '',
            'Compra': total_compra,
            'Ventas': total_ventas,
            'Existencia': total_existencia,
            'Rotación': f'{rotacion_tienda}%'
        })
    
    return pd.DataFrame(resultados)

# Pestañas
tab1, tab2, tab3 = st.tabs(["📋 Reporte Detallado", "📊 Análisis por Tienda", "📈 Gráficos"])

with tab1:
    st.subheader("Reporte Detallado por Tienda y Modelo")
    
    df_reporte = crear_tabla_con_totales(df_filtrado)
    
    # Aplicar estilos
    def highlight_totals(row):
        if 'Total' in str(row['Tienda']) or 'Total' in str(row['Modelo']):
            return ['background-color: #e6f3ff; font-weight: bold'] * len(row)
        elif str(row['Tienda']).startswith('▼'):
            return ['background-color: #f0f0f0; font-weight: bold'] * len(row)
        return [''] * len(row)
    
    st.dataframe(
        df_reporte.style.apply(highlight_totals, axis=1),
        use_container_width=True,
        height=600,
        hide_index=True
    )

with tab2:
    st.subheader("Resumen por Tienda")
    
    # Agrupar por tienda
    df_tiendas = df_filtrado.groupby('Tienda').agg({
        'Compra': 'sum',
        'Ventas': 'sum',
        'Existencia': 'sum',
        'Rotación_num': 'mean'
    }).reset_index()
    
    df_tiendas['Rotación'] = df_tiendas['Rotación_num'].round().astype(int).astype(str) + '%'
    df_tiendas = df_tiendas.drop('Rotación_num', axis=1)
    df_tiendas = df_tiendas.sort_values('Ventas', ascending=False)
    
    st.dataframe(df_tiendas, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("Resumen por Producto")
    
    # Agrupar por descripción
    df_productos = df_filtrado.groupby('Descripción').agg({
        'Compra': 'sum',
        'Ventas': 'sum',
        'Existencia': 'sum',
        'Rotación_num': 'mean'
    }).reset_index()
    
    df_productos['Rotación'] = df_productos['Rotación_num'].round().astype(int).astype(str) + '%'
    df_productos = df_productos.drop('Rotación_num', axis=1)
    df_productos = df_productos.sort_values('Ventas', ascending=False)
    
    st.dataframe(df_productos, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Visualización de Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Ventas por Tienda")
        df_chart = df_filtrado.groupby('Tienda')['Ventas'].sum().sort_values(ascending=True)
        st.bar_chart(df_chart)
        
        st.markdown("#### Compra vs Ventas por Tienda")
        df_comp = df_filtrado.groupby('Tienda')[['Compra', 'Ventas']].sum()
        st.bar_chart(df_comp)
    
    with col2:
        st.markdown("#### Existencia por Tienda")
        df_exist = df_filtrado.groupby('Tienda')['Existencia'].sum().sort_values(ascending=True)
        st.bar_chart(df_exist)
        
        st.markdown("#### Rotación por Producto")
        df_rot = df_filtrado.groupby('Descripción')['Rotación_num'].mean().sort_values(ascending=True)
        st.bar_chart(df_rot)

# Footer
st.markdown("---")
st.markdown(f"📅 Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
st.markdown("💡 Usa los filtros de la izquierda para personalizar el reporte")

# Botón de descarga
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Exportar Datos")

csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Descargar CSV",
    data=csv,
    file_name=f'reporte_inventario_{datetime.now().strftime("%Y%m%d")}.csv',
    mime='text/csv',
)