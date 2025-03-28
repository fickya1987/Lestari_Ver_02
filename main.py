# main.py (flat structure version)
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from huggingface_hub import login

# Local imports (assuming files are in same directory)
from constraint1 import highlight_text
from constraint2 import process_and_translate

def main():
    # Initialization
    load_dotenv()
    try:
        login(token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        st.stop()

    # Load data
    try:
        df_kamus = pd.read_excel("dataset/data_kamus 27-3-25.xlsx")
        df_idiom = pd.read_excel("dataset/idiom 27-3-25.xlsx")
        df_paribasa = pd.read_excel("dataset/paribasa 27-3-25.xlsx")
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        st.stop()

    # App UI
    st.title("Lestari2 Beta")
    
    tab1, tab2 = st.tabs(["Translator", "Chatbot"])
    
    with tab1:
        text = st.text_area("Enter text:")
        if st.button("Translate"):
            translated = process_and_translate(df_kamus, df_idiom, df_paribasa, text)
            highlighted = highlight_text(translated, df_kamus)
            st.markdown(highlighted, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
