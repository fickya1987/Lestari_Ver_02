import streamlit as st
from PIL import Image
import pandas as pd
from constraint1 import highlight_text
from constraint2 import process_and_translate

# Page config and styling
st.set_page_config(page_title="Lestari2 Beta", page_icon="📌", layout="wide")

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
        font-size: 4em;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    # Load your data files here
    df_kamus = pd.read_excel("data/kamus.xlsx")
    df_idiom = pd.read_excel("data/idiom.xlsx")
    df_paribasa = pd.read_excel("data/paribasa.xlsx")
    return df_kamus, df_idiom, df_paribasa

def main():
    load_css()
    df_kamus, df_idiom, df_paribasa = load_data()
    
    st.title("Selamat Datang di Lestari2 Beta")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Indo-Sunda", 
        "Sunda-Indo", 
        "Chatbot Syahmi", 
        "Chatbot Yogi"
    ])
    
    with tab1:
        st.header("Translasi Indonesia ke Sunda")
        input_text = st.text_area("Masukkan teks Indonesia:")
        if st.button("Terjemahkan"):
            translated = process_and_translate(df_kamus, df_idiom, df_paribasa, input_text)
            highlighted = highlight_text(translated, df_kamus)
            st.markdown(highlighted, unsafe_allow_html=True)
    
    with tab2:
        st.header("Translasi Sunda ke Indonesia")
        # Similar implementation as tab1
    
    with tab3:
        st.header("Chatbot Sunda")
        # Implement chatbot interface
    
    with tab4:
        st.header("Chatbot Indonesia-Sunda")
        # Implement chatbot interface

if __name__ == "__main__":
    main()
