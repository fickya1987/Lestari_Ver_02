import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from huggingface_hub import login
from constraints import highlight_text  # Updated import
from constraints import process_and_translate
from ai_services import Chatbot, IndoToSundaTranslator, SundaToIndoTranslator

# --- Initialization ---
def initialize_app():
    """Initialize application and authenticate services"""
    try:
        load_dotenv()
        login(token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
        st.session_state.initialized = True
    except Exception as e:
        st.error(f"Initialization failed: {str(e)}")
        st.stop()

# --- UI Configuration ---
def configure_ui():
    """Configure Streamlit UI settings"""
    st.set_page_config(
        page_title="Lestari2 Beta",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E2F;
        color: white;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #2E2E3F !important;
        color: white !important;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    .tab-content {
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_resource
def load_resources():
    """Load required data resources"""
    try:
        df_kamus = pd.read_excel("data/kamus.xlsx")
        df_idiom = pd.read_excel("data/idiom.xlsx")
        df_paribasa = pd.read_excel("data/paribasa.xlsx")
        return df_kamus, df_idiom, df_paribasa
    except Exception as e:
        st.error(f"Data loading failed: {str(e)}")
        st.stop()

# --- Feature Modules ---
def translation_tab(title, direction, df_dict):
    """Generic translation tab component"""
    with st.container():
        st.header(title)
        col1, col2 = st.columns(2)
        
        with col1:
            input_text = st.text_area(
                f"Masukkan teks ({direction[0]}):",
                height=200,
                key=f"input_{direction}"
            )
            
        with col2:
            if st.button(f"Terjemahkan → {direction[1]}", key=f"btn_{direction}"):
                if input_text.strip():
                    with st.spinner("Memproses..."):
                        try:
                            translated = process_and_translate(
                                df_dict['kamus'],
                                df_dict['idiom'],
                                df_dict['paribasa'],
                                input_text
                            )
                            highlighted = highlight_text(translated, df_dict['kamus'])
                            st.markdown(highlighted, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.warning("Masukkan teks terlebih dahulu")

def chatbot_tab(df_kamus):
    """Chatbot interface component"""
    st.header("💬 Chatbot Lestari")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ketik pesan..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Menghasilkan respon..."):
                try:
                    chatbot = Chatbot("your-model-name")
                    response = chatbot.chat(prompt)
                    highlighted = highlight_text(response, df_kamus)
                    st.markdown(highlighted, unsafe_allow_html=True)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": highlighted}
                    )
                except Exception as e:
                    st.error(f"Chatbot error: {str(e)}")

# --- Main Application ---
def main():
    # Initialize application
    if not getattr(st.session_state, 'initialized', False):
        initialize_app()
    
    configure_ui()
    
    # Load resources
    df_kamus, df_idiom, df_paribasa = load_resources()
    df_dict = {
        'kamus': df_kamus,
        'idiom': df_idiom,
        'paribasa': df_paribasa
    }
    
    # App title
    st.title("🌿 Lestari2 Beta")
    st.caption("Platform Pembelajaran Bahasa Sunda Berbasis AI")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "🇮🇩→🇸🇩 Indonesia-Sunda",
        "🇸🇩→🇮🇩 Sunda-Indonesia",
        "💬 Chatbot"
    ])
    
    with tab1:
        translation_tab(
            "Terjemahan Indonesia-Sunda",
            ("Indonesia", "Sunda"),
            df_dict
        )
    
    with tab2:
        translation_tab(
            "Terjemahan Sunda-Indonesia",
            ("Sunda", "Indonesia"),
            df_dict
        )
    
    with tab3:
        chatbot_tab(df_kamus)
    
    # Footer
    st.divider()
    st.caption("© 2023 Lestari2 Beta | Versi 1.0.0")

if __name__ == "__main__":
    main()
