import streamlit as st 
import pandas as pd 
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns 
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Cargar el archivo CSV (usando datos existentes)
df = pd.read_csv("data_set.csv", parse_dates=["fecha"])

# Recalcular 'venta_total' si no existe o hay errores
if 'venta_total' not in df.columns or df['venta_total'].isnull().any():
    df['venta_total'] = df['cantidad'] * df['precio_unitario']

# Verificar que los datos se cargaron correctamente
print(f"Shape del dataset: {df.shape} ")
print("\nPrimeras filas: ")
print(df.head())
print("\nInformación General: ")
print(df.info())
print("\nEstadísticas descriptivas: ")
print(df.describe())
