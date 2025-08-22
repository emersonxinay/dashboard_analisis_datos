import streamlit as st 
import pandas as pd 
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns 
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# creamos datos sinteticos 
np.random.seed(42)
fechas = pd.date_range('2023-01-01', '2024-12-31', freq='D')
n_productos = ['Laptop', 'Mouse', 'Monitor', 'Auriculares']
regiones = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro', 'Oriente']


# generando dataset 
data = []
for fecha in fechas:
    for _ in range(np.random.poisson(10)):
        data.append(
            {
                'fecha': fecha,
                'producto': np.random.choice(n_productos),
                'region': np.random.choice(regiones),
                'cantidad': np.random.randint(1,6),
                'precio_unitario': np.random.uniform(50,1500),
                'vendedor': f'vendedor {np.random.randint(1, 21)}'
            }
        )

df = pd.DataFrame(data)
df['venta_total'] = df['cantidad'] * df['precio_unitario']

print(f"Shape del dataset: {df.shape} ")
print("\nPrimeras filas: ")
print(df.head())
print("\nInformación General: ")
print(df.info())
print("\nEstadisticas descriptivas: ")
print(df.describe())

# ventas por mes 
print("Ventas por mes")
df_mes = df.groupby(df['fecha'].dt.to_period('M'))['venta_total'].sum().reset_index()
df_mes['fecha']=df_mes['fecha'].astype(str)
print(df_mes)

fig_mes = px.line(df_mes, x ='fecha', y='venta_total',
                  title='Tendencia de ventas mensuales',
                  labels ={'venta_total':'Ventas ($)', 'fecha':'Mes'}
                  )
fig_mes.update_traces(line=dict(width=3))
# fig_mes.show()

# top de productos
df_productos = df.groupby('producto')['venta_total'].sum().sort_values(ascending=True)
fig_productos = px.bar(x=df_productos.values, y=df_productos.index,
                       orientation='h', title='Ventas por producto', 
                       labels={'x':'Ventas totales ($)', 'y':'Producto'})

# fig_productos.show()

# analísis geográfico 
df_regiones = df.groupby('region')['venta_total'].sum().reset_index()
fig_regiones = px.pie(df_regiones, values='venta_total', names='region', title='Distribución de ventas por región')

# fig_regiones.show()

# Correlación entre variables 
df_corr = df[['cantidad', 'precio_unitario', 'venta_total']].corr()
fig_corrmap = px.imshow(df_corr, text_auto=True, aspect="auto",
                        title='Correlación entre variables numéricas')
# fig_corrmap.show()

# distribusión de ventas 
fig_dist = px.histogram(df, x = 'venta_total', nbins=50, 
                        title='Distribución de ventas individuales')

# fig_dist.show()

# Iniciar a configurar nuestra página web con dashboard
# para el icono de la pestaña de la web
st.set_page_config(page_title="Dashboard de Ventas", page_icon="📊" , layout="wide")
# Estilo personalizado para cambiar color de fondo


# titulo principal
st.title("📊 Dashboard de Analísis de Ventas")
st.title("Código Futuro - 2025")
st.markdown("---")

# barras laterales para los filtros
st.sidebar.header("Filtros")
productos_seleccionados = st.sidebar.multiselect(
    "Selecciona Productos",
    options=df['producto'].unique(),
    default=df['producto'].unique()
)
regiones_seleccionados = st.sidebar.multiselect(
    "Selecciona Región",
    options=df['region'].unique(),
    default=df['region'].unique()
)

# filtrar datos basados en selección
df_filtered = df[
    (df['producto'].isin(productos_seleccionados)) &
    (df['region'].isin(regiones_seleccionados))
]

# metricas principales
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Ventas Totales", f"${df_filtered['venta_total'].sum():,.0f}")
with col2:
    st.metric("Promedio por venta", f"${df_filtered['venta_total'].mean():.0f}")
with col3:
    st.metric("Nùmero de ventas", f"{len(df_filtered):,}" )
with col4:
    crecimiento = ((df_filtered[df_filtered['fecha'] >= '2024-01-01']['venta_total'].sum()/
                    df_filtered[df_filtered['fecha']<'2024-01-01']['venta_total'].sum())-1)*100
    
    st.metric("Crecimiento 2024", f"{crecimiento:.1f}%")


# layouts con 2 columnas 
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_mes, use_container_width=True)
    st.plotly_chart(fig_productos, use_container_width=True)
with col2:
    st.plotly_chart(fig_regiones, use_container_width=True)
    st.plotly_chart(fig_corrmap, use_container_width=True)

# Grafico completo en la parte superior
st.plotly_chart(fig_dist, use_container_width=True)
