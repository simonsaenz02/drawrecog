import os
import streamlit as st
import base64
from openai import OpenAI

# =======================
# Función para codificar imagen en base64
# =======================
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


# =======================
# Configuración inicial de la página
# =======================
st.set_page_config(
    page_title="Análisis de Imagen",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =======================
# CSS personalizado (colores y estilos)
# =======================
st.markdown("""
    <style>
        /* Fondo degradado */
        .stApp {
            background: linear-gradient(135deg, #1f1c2c, #928DAB);
            color: #ffffff;
        }

        /* Títulos principales */
        h1 {
            text-align: center;
            font-size: 2.5em;
            color: #FFD700;
            text-shadow: 1px 1px 3px black;
        }

        /* Subtítulos */
        h2, h3 {
            color: #87CEEB;
        }

        /* Cuadro de texto y widgets */
        .stTextInput>div>div>input,
        .stTextArea textarea {
            background-color: #2e2e3e;
            color: white;
            border-radius: 10px;
            border: 1px solid #555;
        }

        /* Botón */
        div.stButton > button {
            background-color: #FF8C00;
            color: white;
            border-radius: 12px;
            border: none;
            font-size: 1em;
            padding: 0.6em 1.2em;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: #FF4500;
            transform: scale(1.05);
        }

        /* Expander */
        .streamlit-expanderHeader {
            font-weight: bold;
            color: #FFD700;
        }

        /* Mensaje del resultado */
        .result-box {
            background-color: #2e2e3e;
            padding: 15px;
            border-radius: 12px;
            margin-top: 20px;
            color: #ffffff;
            border-left: 5px solid #FF8C00;
        }
    </style>
""", unsafe_allow_html=True)


# =======================
# Interfaz
# =======================
st.title("🔎 Análisis de Imagen con IA 🤖🏞️")

st.write("Sube una imagen y deja que la IA te cuente lo que ve. "
         "Si quieres, puedes darle un contexto adicional para un análisis más detallado.")

ke = st.text_input('🔑 Ingresa tu Clave de API')
os.environ['OPENAI_API_KEY'] = ke

# API Key
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# Upload file
uploaded_file = st.file_uploader("📂 Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("👁️ Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Extra context
show_details = st.toggle("📝 ¿Quieres preguntar algo específico?", value=False)

if show_details:
    additional_details = st.text_area("✍️ Escribe tu contexto aquí:")

# Button
analyze_button = st.button("🚀 Analizar imagen")

# =======================
# Lógica de análisis
# =======================
if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("🔍 Analizando... por favor espera"):
        base64_image = encode_image(uploaded_file)

        prompt_text = "Describe lo que ves en la imagen en español."

        if show_details and additional_details:
            prompt_text += f"\n\nContexto adicional:\n{additional_details}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]

        try:
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(
                        f"<div class='result-box'>{full_response}▌</div>",
                        unsafe_allow_html=True
                    )
            message_placeholder.markdown(
                f"<div class='result-box'>{full_response}</div>",
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

else:
    if not uploaded_file and analyze_button:
        st.warning("⚠️ Por favor sube una imagen.")
    if not api_key:
        st.warning("⚠️ Ingresa tu API key.")
