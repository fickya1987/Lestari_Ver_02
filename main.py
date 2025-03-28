import streamlit as st
from PIL import Image
import pandas as pd
import os
from dotenv import load_dotenv
from huggingface_hub import login
from constraint1 import highlight_text
from constraint2 import process_and_translate
from ai_services import Chatbot, IndoToSundaTranslator, SundaToIndoTranslator

# Initialize environment and Hugging Face login
load_dotenv()

def initialize_app():
    """Initialize application and authenticate with Hugging Face"""
    try:
        login(token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
        st.success("Successfully connected to Hugging Face Hub")
    except Exception as e:
        st.error(f"Failed to authenticate with Hugging Face: {str(e)}")
        st.stop()

# Page config and styling
st.set_page_config(
    page_title="Lestari2 Beta", 
    page_icon="📌", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E2F;
        color: white;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
    }
    .title {
        color: white;
        font-size: 2.5em;
        text-align: center;
        margin-bottom: 20px;
    }
    .tab-content {
        padding: 20px;
        background-color: #2E2E3F;
        border-radius: 10px;
        margin-top: 15px;
    }
    .stTextArea textarea {
        background-color: #3E3E4F !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_data():
    """Load dictionary data with caching"""
    try:
        df_kamus = pd.read_excel("data/kamus.xlsx")
        df_idiom = pd.read_excel("data/idiom.xlsx")
        df_paribasa = pd.read_excel("data/paribasa.xlsx")
        return df_kamus, df_idiom, df_paribasa
    except Exception as e:
        st.error(f"Failed to load data files: {str(e)}")
        st.stop()

def indo_sunda_tab(df_kamus, df_idiom, df_paribasa):
    """Indonesia to Sunda translation tab"""
    st.header("🇮🇩 → 🇸🇩 Indonesia to Sunda Translator")
    input_text = st.text_area(
        "Masukkan teks dalam Bahasa Indonesia:",
        height=150,
        placeholder="Ketik atau tempel teks disini..."
    )
    
    if st.button("Terjemahkan", key="indo_sunda_btn"):
        if not input_text.strip():
            st.warning("Masukkan teks terlebih dahulu")
            return
        
        with st.spinner("Sedang menerjemahkan..."):
            try:
                translated = process_and_translate(
                    df_kamus, df_idiom, df_paribasa, input_text
                )
                highlighted = highlight_text(translated, df_kamus)
                st.subheader("Hasil Terjemahan:")
                st.markdown(highlighted, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Terjadi kesalahan saat menerjemahkan: {str(e)}")

def sunda_indo_tab():
    """Sunda to Indonesia translation tab"""
    st.header("🇸🇩 → 🇮🇩 Sunda to Indonesia Translator")
    # Similar implementation as indo_sunda_tab
    # ...

def chatbot_tab(df_kamus):
    """Chatbot interface tab"""
    st.header("💬 Chatbot Lestari")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input area
    if prompt := st.chat_input("Ketik pesan dalam Bahasa Sunda..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display bot response
        with st.chat_message("assistant"):
            with st.spinner("Sedang memproses..."):
                try:
                    chatbot = Chatbot("your-model-name")
                    response = chatbot.chat(prompt)
                    highlighted = highlight_text(response, df_kamus)
                    st.markdown(highlighted, unsafe_allow_html=True)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": highlighted}
                    )
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

def main():
    initialize_app()
    load_css()
    df_kamus, df_idiom, df_paribasa = load_data()
    
    st.title("🌿 Lestari2 Beta")
    st.markdown("Aplikasi pembelajaran Bahasa Sunda berbasis AI")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "Terjemahan Indonesia-Sunda", 
        "Terjemahan Sunda-Indonesia", 
        "Chatbot Sunda"
    ])
    
    with tab1:
        indo_sunda_tab(df_kamus, df_idiom, df_paribasa)
    
    with tab2:
        sunda_indo_tab()
    
    with tab3:
        chatbot_tab(df_kamus)
    
    # Add footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #888;'>"
        "© 2023 Lestari2 Beta | Versi 1.0.0"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
