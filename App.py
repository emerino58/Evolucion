import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.animation import FuncAnimation, PillowWriter
from PIL import Image
import tempfile
import numpy as np
import base64

# === FONDO CON IMAGEN Y TEXTO NEGRO ===
def set_background(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: black;
        }}
        h1, h2, h3, h4, h5, h6, p, span, div {{
            color: black !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("Fondo.png")

# === ESTILO PARA SELECTORES Y GRÁFICO FINAL ===
st.markdown("""
    <style>
    .select-container {
        border: 2px solid #0077b6;
        padding: 10px;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.6);
        margin-bottom: 20px;
    }

    .plot-container {
        border: 3px solid #023e8a;
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.9);
        margin-top: 30px;
    }

    .stSelectbox > div {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# === TÍTULO ===
st.title("Evolución de Puntajes")
st.markdown("### Campeonato ITAU 2024")

# === CARGAR DATOS ===
@st.cache_data
def cargar_datos():
    df = pd.read_excel("NW_Puntaje.xlsx")
    fechas = [col for col in df.columns if col.startswith("Fecha_")]
    return df, fechas

puntaje_df, fechas = cargar_datos()

# === SELECTORES CON MARCO ===
with st.container():
    st.markdown('<div class="select-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        equipo1 = st.selectbox("Selecciona el primer equipo", puntaje_df["Equipo"].tolist(), index=0)
    with col2:
        equipo2 = st.selectbox("Selecciona el segundo equipo", puntaje_df["Equipo"].tolist(), index=1)
    st.markdown('</div>', unsafe_allow_html=True)

# === DATOS DE EQUIPOS ===
def obtener_datos(equipo):
    fila = puntaje_df[puntaje_df["Equipo"] == equipo].iloc[0]
    puntajes = fila[fechas].tolist()
    logo = os.path.join("Logos", fila["Logo_Club"])
    return puntajes, logo

puntajes1, logo1_path = obtener_datos(equipo1)
puntajes2, logo2_path = obtener_datos(equipo2)

# === MOSTRAR LOGOS ===
col1, col2 = st.columns(2)
with col1:
    st.image(Image.open(logo1_path), caption=equipo1, width=150)
with col2:
    st.image(Image.open(logo2_path), caption=equipo2, width=150)

# === ANIMACIÓN GIF ===
fig, ax = plt.subplots()
line1, = ax.plot([], [], label=equipo1)
line2, = ax.plot([], [], label=equipo2)
ax.set_xlim(1, len(fechas))
ax.set_ylim(0, max(max(puntajes1), max(puntajes2)) + 5)
ax.set_xlabel("Fecha")
ax.set_ylabel("Puntaje")
ax.legend()
ax.grid(True)

def animate(i):
    x = list(range(1, i+2))
    y1 = puntajes1[:i+1]
    y2 = puntajes2[:i+1]
    line1.set_data(x, y1)
    line2.set_data(x, y2)
    return line1, line2

with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as tmpfile:
    ani = FuncAnimation(fig, animate, frames=len(fechas), interval=300, blit=True)
    writer = PillowWriter(fps=3)  # loop=0 si matplotlib >= 3.6
    ani.save(tmpfile.name, writer=writer, savefig_kwargs={'facecolor': 'white'})
    plt.close(fig)
    st.image(tmpfile.name, caption="Evolución animada")

