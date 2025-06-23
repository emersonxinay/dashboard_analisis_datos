import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Función para calcular la nota de asistencia
def calcular_nota_asistencia(porcentaje_asistencia):
    if porcentaje_asistencia >= 80:
        return 7
    elif porcentaje_asistencia >= 60:
        return 6 + (porcentaje_asistencia - 60) / 20  # Decimales entre 6 y 7
    elif porcentaje_asistencia >= 40:
        return 5 + (porcentaje_asistencia - 40) / 20  # Decimales entre 5 y 6
    elif porcentaje_asistencia >= 20:
        return 4 + (porcentaje_asistencia - 20) / 20  # Decimales entre 4 y 5
    else:
        return 1

# Función para procesar el archivo CSV
def procesar_archivo(file):
    # Leer el archivo CSV
    df = pd.read_csv(file)
    
    # Limpiar y convertir las notas
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
    
    # Reemplazar valores faltantes por 0 para promediar correctamente
    df[["nota1", "nota 2"]] = df[["nota1", "nota 2"]].fillna(0)

    # Calcular promedio de notas
    df["promedio"] = df[["nota1", "nota 2"]].mean(axis=1)
    
    # Calcular porcentaje de asistencia
    asist_cols = [col for col in df.columns if col.startswith("asistencia")]
    df["asistencias_P"] = df[asist_cols].apply(lambda row: (row == "P").sum(), axis=1)
    df["total_asistencias"] = df[asist_cols].notna().sum(axis=1)
    df["porcentaje_asistencia"] = round((df["asistencias_P"] / df["total_asistencias"]) * 100, 2)
    
    # Asignar nota de asistencia
    df["nota_asistencia"] = df["porcentaje_asistencia"].apply(calcular_nota_asistencia)
    
    # Calcular promedio final
    df["promedio_final"] = (2 * df["promedio"] + df["nota_asistencia"]) / 3
    
    # Redondear el promedio final
    df["promedio_final_redondeado"] = df["promedio_final"].round(1)
    
    # Calcular promedio general del curso y asistencia general
    promedio_general = df["promedio_final_redondeado"].mean()
    asistencia_general = df["porcentaje_asistencia"].mean()
    
    return df, promedio_general, asistencia_general

# Configuración de la interfaz de Streamlit
st.title("📊 Dashboard de Asistencia y Notas - 4°A")

# Cargar el archivo CSV
uploaded_file = st.file_uploader("📂 Cargar archivo CSV", type=["csv"])

if uploaded_file is not None:
    # Procesar el archivo CSV cargado
    df, promedio_general, asistencia_general = procesar_archivo(uploaded_file)
    
    # Mostrar los resultados generales
    st.subheader("📊 Promedio y Asistencia General")
    st.write(f"Promedio general del curso: {promedio_general:.2f}")
    st.write(f"Porcentaje de asistencia general: {asistencia_general:.2f}%")
    
    # Mostrar la tabla de datos procesados
    with st.expander("📋 Ver tabla de datos"):
        st.dataframe(df[[
            "N°", "NOMBRES", "nota1", "nota 2", "promedio",
            "porcentaje_asistencia", "nota_asistencia",
            "promedio_final", "promedio_final_redondeado"
        ]])
    
    # Gráfico de notas promedio
    st.subheader("📈 Promedio de Notas")
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
    
    # Gráfico de promedios en función de asistencia
    st.subheader("📊 Promedio Final por Asistencia")
    df_asistencia_promedio = df[df["NOMBRES"].notna() & df["promedio_final_redondeado"].notna()]
    if not df_asistencia_promedio.empty:
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        ax3.scatter(df_asistencia_promedio["porcentaje_asistencia"], df_asistencia_promedio["promedio_final_redondeado"], color="orange")
        ax3.set_ylabel("Promedio Final (Redondeado)")
        ax3.set_xlabel("% Asistencia")
        ax3.set_title("Promedio Final vs Asistencia")
        st.pyplot(fig3)
    else:
        st.warning("⚠️ No hay datos válidos para graficar promedios en función de la asistencia.")
    
    # Filtros extra
    st.subheader("🔎 Filtrar por estudiante")
    if "NOMBRES" in df.columns and not df["NOMBRES"].dropna().empty:
        nombre_filtrado = st.selectbox("Selecciona un estudiante", df["NOMBRES"].dropna())
        st.write(df[df["NOMBRES"] == nombre_filtrado][[
            "nota1", "nota 2", "promedio",
            "porcentaje_asistencia", "nota_asistencia",
            "promedio_final", "promedio_final_redondeado"
        ]])
    else:
        st.info("No hay estudiantes disponibles para filtrar.")
else:
    st.info("Por favor, carga un archivo CSV para comenzar.")
