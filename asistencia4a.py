import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Cargar CSV
df = pd.read_csv("asistencia4a.csv")

# Limpiar y convertir notas
df["nota1"] = (
    df["nota1"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .replace("#DIV/0!", pd.NA)
)
df["nota 2"] = (
    df["nota 2"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .replace("#DIV/0!", pd.NA)
)

# Convertir a float usando to_numeric para evitar errores
df["nota1"] = pd.to_numeric(df["nota1"], errors="coerce")
df["nota 2"] = pd.to_numeric(df["nota 2"], errors="coerce")

# Calcular promedio de notas
df["promedio"] = df[["nota1", "nota 2"]].mean(axis=1)

# Calcular porcentaje de asistencia
asist_cols = [col for col in df.columns if col.startswith("asistencia")]
df["asistencias_P"] = df[asist_cols].apply(lambda row: (row == "P").sum(), axis=1)
df["total_asistencias"] = df[asist_cols].notna().sum(axis=1)
df["porcentaje_asistencia"] = round((df["asistencias_P"] / df["total_asistencias"]) * 100, 2)

# -----------------------------
# INTERFAZ STREAMLIT
# -----------------------------
st.title("📊 Dashboard de Asistencia y Notas - 4°A")
st.write("Datos procesados desde el archivo CSV")

# Mostrar tabla general
with st.expander("📋 Ver tabla de datos"):
    st.dataframe(df[["N°", "NOMBRES", "nota1", "nota 2", "promedio", "porcentaje_asistencia"]])

# Gráfico de notas promedio
st.subheader("📈 Promedio de Notas")

# Validación para evitar error de longitudes
df_notas = df[df["NOMBRES"].notna() & df["promedio"].notna()]
if not df_notas.empty:
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    ax1.bar(df_notas["NOMBRES"], df_notas["promedio"], color="skyblue")
    ax1.set_ylabel("Promedio")
    ax1.set_xlabel("Estudiantes")
    ax1.set_title("Promedio de notas por estudiante")
    plt.xticks(rotation=90)
    st.pyplot(fig1)
else:
    st.warning("⚠️ No hay datos válidos para graficar el promedio de notas.")

# Gráfico de asistencia
st.subheader("✅ Porcentaje de Asistencia")

df_asistencia = df[df["NOMBRES"].notna() & df["porcentaje_asistencia"].notna()]
if not df_asistencia.empty:
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.bar(df_asistencia["NOMBRES"], df_asistencia["porcentaje_asistencia"], color="green")
    ax2.set_ylabel("% Asistencia")
    ax2.set_xlabel("Estudiantes")
    ax2.set_title("Porcentaje de asistencia por estudiante")
    plt.xticks(rotation=90)
    st.pyplot(fig2)
else:
    st.warning("⚠️ No hay datos válidos para graficar porcentaje de asistencia.")

# Filtros extra
st.subheader("🔎 Filtrar por estudiante")

if "NOMBRES" in df.columns and not df["NOMBRES"].dropna().empty:
    nombre_filtrado = st.selectbox("Selecciona un estudiante", df["NOMBRES"].dropna())
    st.write(df[df["NOMBRES"] == nombre_filtrado][["nota1", "nota 2", "promedio", "porcentaje_asistencia"]])
else:
    st.info("No hay estudiantes disponibles para filtrar.")
