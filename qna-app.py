import streamlit as st
from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

# Cargar las variables de entorno
load_dotenv()
ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
ai_key = os.getenv('AI_SERVICE_KEY')
ai_project_name = os.getenv('QA_PROJECT_NAME')
ai_deployment_name = os.getenv('QA_DEPLOYMENT_NAME')

# Crear cliente de Azure
credential = AzureKeyCredential(ai_key)
ai_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=credential)

# Configuración de Streamlit
st.set_page_config(page_title="AI Financial Q&A", page_icon="💰", layout="centered")

# CSS para un diseño minimalista y profesional
st.markdown("""
    <style>
        body {
            background-color: #f7f7f7;
            font-family: 'Arial', sans-serif;
        }
        .chat-container {
            background: #ffffff;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
        }
        .chat-title {
            text-align: center;
            font-size: 2.5em;
            color: #white;
            margin-bottom: 2rem;
        }
        .message-container {
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 1.5rem;
            margin-top: 1rem;
        }
        .message {
            padding: 1rem;
            border-radius: 12px;
            max-width: 80%;
            word-wrap: break-word;
            margin-bottom: 1rem;
        }
        .user-message {
            background: #3498db;
            color: white;
            margin-left: auto;
        }
        .bot-message {
            background: #ecf0f1;
            color: #2c3e50;
            margin-right: auto;
        }
        .stTextInput>div>div>input {
            border-radius: 30px;
            padding: 1rem;
            font-size: 1rem;
        }
        .stButton>button {
            background-color: #3498db;
            color: white;
            padding: 1rem 2rem;
            border-radius: 30px;
            font-size: 1.1rem;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #2980b9;
        }
    </style>
""", unsafe_allow_html=True)

# Título y explicación de la aplicación
st.markdown('<div class="chat-title">💰 AI Financial Assistant</div>', unsafe_allow_html=True)
st.write("¡Hazme cualquier pregunta sobre finanzas y te proporcionaré la mejor respuesta!")

# Iniciar historial de conversación
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Función para manejar la entrada y salida
def get_answer_from_azure(question):
    try:
        # Obtener respuesta de Azure AI
        response = ai_client.get_answers(
            question=question,
            project_name=ai_project_name,
            deployment_name=ai_deployment_name
        )

        if response.answers:
            # Mostrar la primera respuesta y su metadato
            candidate = response.answers[0]
            return candidate.answer, candidate.confidence, candidate.source
        else:
            return "No se encontraron respuestas. ¿Podrías reformular la pregunta?", None, None
    except Exception as e:
        return f"Error al obtener respuesta: {str(e)}", None, None

# Formulario de entrada de preguntas
with st.form(key="question_form"):
    user_question = st.text_input("Tu pregunta sobre finanzas:", key="input", placeholder="Escribe tu pregunta aquí...")
    submit_button = st.form_submit_button(label="Enviar")

# Si el usuario ha enviado una pregunta
if submit_button and user_question:
    # Mostrar la pregunta del usuario
    st.session_state.messages.append(f"👤: {user_question}")
    
    # Obtener la respuesta de Azure
    answer, confidence, source = get_answer_from_azure(user_question)
    
    # Mostrar la respuesta del bot
    st.session_state.messages.append(f"🤖: {answer}")
    
    # Mostrar los metadatos de confianza y fuente si están disponibles
    if confidence is not None:
        st.session_state.messages.append(f"Confianza: {confidence * 100:.1f}%")
    if source:
        st.session_state.messages.append(f"Fuente: {source}")

# Mostrar todo el historial de conversación
with st.container():
    # chat_container = st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Historial del chat
    message_container = st.markdown('<div class="message-container">', unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        if message.startswith("👤"):
            st.markdown(f'<div class="message user-message">{message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="message bot-message">{message}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar message-container
    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar chat-container
