# ========== chabotSyahmi.py ==========
import streamlit as st
import pandas as pd
import re
import openai
import os
from bs4 import BeautifulSoup

from AI_chatbot import generate_text
from constraint1 import highlight_text

openai.api_key = os.getenv("OPENAI_API_KEY")  # Pastikan API key tersedia

# UI Styling
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
    display: flex;
    justify-content: center;
    align-items: center;
}
.content { color: white; font-size: 1em; }
label, input, ::placeholder { color: white !important; background-color: black !important; }
</style>
""", unsafe_allow_html=True)

# Load kamus
df_kamus = pd.read_excel("dataset/data_kamus 27-3-25.xlsx")
df_idiom = pd.read_excel("dataset/idiom 27-3-25.xlsx")
df_paribasa = pd.read_excel("dataset/paribasa 27-3-25.xlsx")

st.title("Chatbot Bahasa Sunda Loma")
st.write("Selamat datang! Silakan ajukan pertanyaan dalam bahasa Sunda.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Tulis pesan Anda:")

if st.button("Kirim") and user_input:
    bot_response = generate_text(user_input)
    text_constraint, kata_terdapat, kata_tidak_terdapat, pasangan_kata = highlight_text(
        bot_response, df_kamus
    )
    clean_text = BeautifulSoup(text_constraint, "html.parser").get_text()
    st.session_state.chat_history.append((user_input, clean_text))

for user_msg, bot_msg in st.session_state.chat_history:
    st.markdown(f"**User:** {user_msg}")
    st.markdown(f"**Bot:** {bot_msg}")

