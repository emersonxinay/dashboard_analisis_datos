import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Función para calcular la nota de asistencia
def calcular_nota_asistencia(porcentaje_asistencia):
    if porcentaje_asistencia >= 80:
        return 7
    elif porcentaje_asistencia >= 60:
        return 6 + (porcentaje_asistencia - 60) / 20
    elif porcentaje_asistencia >= 40:
        return 5 + (porcentaje_asistencia - 40) / 20
    elif porcentaje_asistencia >= 20:
        return 4 + (porcentaje_asistencia - 20) / 20
    else:
        return 1

# Función para procesar un archivo individual
def procesar_archivo(file, nombre_archivo):
    df = pd.read_csv(file)
    df["nota1"] = df["nota1"].astype(str).str.replace(",", ".", regex=False).replace("#DIV/0!", pd.NA)
    df["nota 2"] = df["nota 2"].astype(str).str.replace(",", ".", regex=False).replace("#DIV/0!", pd.NA)
    df["nota1"] = pd.to_numeric(df["nota1"], errors="coerce")
    df["nota 2"] = pd.to_numeric(df["nota 2"], errors="coerce")
    df[["nota1", "nota 2"]] = df[["nota1", "nota 2"]].fillna(0)
    df["promedio"] = df[["nota1", "nota 2"]].mean(axis=1)

    asist_cols = [col for col in df.columns if col.startswith("asistencia")]
    df["asistencias_P"] = df[asist_cols].apply(lambda row: (row == "P").sum(), axis=1)
    df["total_asistencias"] = df[asist_cols].notna().sum(axis=1)
    df["porcentaje_asistencia"] = round((df["asistencias_P"] / df["total_asistencias"]) * 100, 2)
    df["nota_asistencia"] = df["porcentaje_asistencia"].apply(calcular_nota_asistencia)
    df["promedio_final"] = (2 * df["promedio"] + df["nota_asistencia"]) / 3
    df["promedio_final_redondeado"] = df["promedio_final"].round(1)
    df["curso"] = nombre_archivo.split(".")[0]
    return df

# --- Interfaz Streamlit ---
st.title("📊 Consolidado de Notas y Asistencias (Varios Cursos)")

uploaded_files = st.file_uploader("📂 Cargar múltiples archivos CSV", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    dfs = []
    for file in uploaded_files:
        nombre_archivo = file.name
        df_temp = procesar_archivo(file, nombre_archivo)
        dfs.append(df_temp)

    df_total = pd.concat(dfs, ignore_index=True)

    promedio_general = df_total["promedio_final_redondeado"].mean()
    asistencia_general = df_total["porcentaje_asistencia"].mean()

    st.subheader("📊 Promedio General Consolidado")
    st.write(f"📈 Promedio general: **{promedio_general:.2f}**")
    st.write(f"✅ Asistencia promedio general: **{asistencia_general:.2f}%**")

    with st.expander("📋 Ver tabla completa de estudiantes"):
        st.dataframe(df_total[[
            "curso", "N°", "NOMBRES", "nota1", "nota 2", "promedio",
            "porcentaje_asistencia", "nota_asistencia", "promedio_final_redondeado"
        ]])

    st.subheader("📈 Promedio por Curso")
    promedio_por_curso = df_total.groupby("curso")["promedio_final_redondeado"].mean()
    fig1, ax1 = plt.subplots()
    promedio_por_curso.plot(kind="bar", ax=ax1, color="skyblue")
    ax1.set_ylabel("Promedio Final")
    ax1.set_title("Promedio final por curso")
    st.pyplot(fig1)

    st.subheader("✅ Asistencia Promedio por Curso")
    asistencia_por_curso = df_total.groupby("curso")["porcentaje_asistencia"].mean()
    fig2, ax2 = plt.subplots()
    asistencia_por_curso.plot(kind="bar", ax=ax2, color="green")
    ax2.set_ylabel("% Asistencia")
    ax2.set_title("Asistencia promedio por curso")
    st.pyplot(fig2)

    # FILTRO POR CURSO
    st.subheader("🔍 Análisis por Curso")
    cursos = df_total["curso"].unique().tolist()
    curso_seleccionado = st.selectbox("Selecciona un curso", cursos)

    df_curso = df_total[df_total["curso"] == curso_seleccionado]

    st.write("### 📋 Detalle del curso seleccionado")
    st.dataframe(df_curso[[
        "N°", "NOMBRES", "nota1", "nota 2", "promedio",
        "porcentaje_asistencia", "nota_asistencia", "promedio_final_redondeado"
    ]])

    # 🎯 NUEVOS GRÁFICOS DETALLADOS PARA EL CURSO
    st.write("## 📊 Gráficos detallados")

    # 1. Histograma de promedios finales
    st.write("### 📉 Distribución de promedios finales")
    fig_hist, ax_hist = plt.subplots()
    ax_hist.hist(df_curso["promedio_final_redondeado"], bins=7, color="lightcoral", edgecolor="black")
    ax_hist.set_xlabel("Promedio Final")
    ax_hist.set_ylabel("Cantidad de estudiantes")
    ax_hist.set_title("Distribución de promedios finales")
    st.pyplot(fig_hist)

    # 2. Scatter: promedio vs asistencia
    st.write("### 🎯 Relación Promedio Final vs % Asistencia")
    fig_scatter, ax_scatter = plt.subplots()
    ax_scatter.scatter(df_curso["porcentaje_asistencia"], df_curso["promedio_final_redondeado"], color="purple")
    ax_scatter.set_xlabel("% Asistencia")
    ax_scatter.set_ylabel("Promedio Final")
    ax_scatter.set_title("Promedio vs Asistencia")
    st.pyplot(fig_scatter)

    # 3. Barras comparando nota1 y nota2 por estudiante
    st.write("### 📊 Comparación Nota 1 vs Nota 2")
    fig_notas, ax_notas = plt.subplots(figsize=(10, 4))
    nombres = df_curso["NOMBRES"]
    x = range(len(nombres))
    ax_notas.bar(x, df_curso["nota1"], width=0.4, label="Nota 1", align="center")
    ax_notas.bar([i + 0.4 for i in x], df_curso["nota 2"], width=0.4, label="Nota 2", align="center")
    ax_notas.set_xticks([i + 0.2 for i in x])
    ax_notas.set_xticklabels(nombres, rotation=90, fontsize=8)
    ax_notas.set_title("Nota 1 y Nota 2 por estudiante")
    ax_notas.legend()
    st.pyplot(fig_notas)

    # 4. Barras: rangos de promedio final
    st.write("### 📊 Cantidad de estudiantes por rango de promedio")
    bins = [1, 3.9, 4.9, 5.9, 6.9, 7.1]
    labels = ["<4", "4.0–4.9", "5.0–5.9", "6.0–6.9", "7.0"]
    df_curso["rango"] = pd.cut(df_curso["promedio_final_redondeado"], bins=bins, labels=labels, right=False)
    conteo_rangos = df_curso["rango"].value_counts().sort_index()
    fig_rangos, ax_rangos = plt.subplots()
    conteo_rangos.plot(kind="bar", ax=ax_rangos, color="orange")
    ax_rangos.set_ylabel("Cantidad de estudiantes")
    ax_rangos.set_title("Distribución por rangos de promedio")
    st.pyplot(fig_rangos)

else:
    st.info("Sube varios archivos CSV con el mismo formato para ver estadísticas consolidadas.")
