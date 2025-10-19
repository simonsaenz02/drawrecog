import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

# ==============================
# VARIABLES INICIALES
# ==============================
Expert = " "
profile_imgenh = " "

# ==============================
# FUNCIÓN: ENCODEAR IMAGEN EN BASE64
# ==============================
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# ==============================
# CONFIGURACIÓN DE PÁGINA
# ==============================
st.set_page_config(page_title='🎨 Tablero Inteligente', page_icon="🤖")
st.title('🎨 Tablero Inteligente')
st.markdown("""
Bienvenido al **Tablero Inteligente**.  
Aquí podrás **dibujar un boceto** y la inteligencia artificial intentará **interpretar lo que ve**.
""")

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.subheader("ℹ️ Acerca de la app")
    st.write("Esta aplicación demuestra la capacidad de una IA para interpretar un boceto en tiempo real.")
    st.caption("Dibuja en el panel principal y presiona el botón para analizar tu dibujo.")

# ==============================
# PANEL DE DIBUJO
# ==============================
st.subheader("🖌️ Dibuja en el panel y luego analiza tu creación:")

stroke_width = st.sidebar.slider('✏️ Selecciona el ancho de línea', 1, 30, 5)
stroke_color = "#000000"  # Color del trazo
bg_color = '#FFFFFF'      # Fondo blanco

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # color semitransparente para relleno
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

# ==============================
# INGRESO DE API KEY
# ==============================
ke = st.text_input('🔑 Ingresa tu API key de OpenAI', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# ==============================
# CLIENTE DE OPENAI
# ==============================
client = OpenAI(api_key=api_key) if api_key else None

# ==============================
# BOTÓN DE ANÁLISIS
# ==============================
analyze_button = st.button("🔍 Analizar dibujo", type="primary")

if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("⏳ Analizando tu dibujo..."):
        # Guardar y convertir la imagen
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        # Codificar en base64
        base64_image = encode_image_to_base64("img.png")

        # Prompt
        prompt_text = "Describe brevemente en español el contenido del dibujo."

        # Crear payload
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{base64_image}",
                    },
                ],
            }
        ]

        # Solicitud a la API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # modelo seleccionado
                messages=messages,
                max_tokens=500,
            )

            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown("### 📝 Interpretación de la IA:")
                message_placeholder.markdown(full_response)

            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content

        except Exception as e:
            st.error(f"⚠️ Ocurrió un error: {e}")

# ==============================
# MENSAJES DE ADVERTENCIA
# ==============================
else:
    if not api_key:
        st.warning("🔑 Debes ingresar tu API key para continuar.")
    elif analyze_button and canvas_result.image_data is None:
        st.warning("✏️ Por favor dibuja algo en el panel antes de analizar.")

