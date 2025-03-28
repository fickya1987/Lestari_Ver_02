import streamlit as st
import pandas as pd
import re
import openai
import torch
from transformers import pipeline, BitsAndBytesConfig
from huggingface_hub import login

from AI_chatbot import generate_text
from constraint1 import highlight_text

# Menambahkan CSS dengan beberapa opsi warna
st.markdown(
    """
    <style>
    /* Latar belakang aplikasi */
    .stApp {
        background-color: #1E1E2F; /* Latar belakang abu-abu gelap */
        color: white;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;  /* Mengatur warna latar belakang tombol */
    }
    .title {
        color: white;
        font-size: 4em;
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .content {
        color: white;
        font-size: 1em;
    }
    label {
        color: white !important;
    }
    input {
        color: white !important;
        background-color: black !important; /* Jika ingin kotak input hitam */
    }
    ::placeholder { /* Untuk placeholder teks */
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# Nonaktifkan TF32 di CUDA
torch.backends.cuda.matmul.allow_tf32 = False
# Konfigurasi BitsAndBytes untuk kuantisasi 4-bit
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
# Load pipeline tanpa `device="cuda"`
pipe = pipeline(
    "image-text-to-text",
    model="google/gemma-3-12b-it",
    torch_dtype=torch.bfloat16,
    model_kwargs={
        "quantization_config": bnb_config
    },  # Tambahkan konfigurasi kuantisasi
)
print("Model berhasil dimuat dengan 4-bit quantization menggunakan BitsAndBytes!")

# Load data kamus
df_kamus = pd.read_excel("dataset/data_kamus 27-3-25.xlsx")
df_idiom = pd.read_excel("dataset/idiom 27-3-25.xlsx")
df_paribasa = pd.read_excel("dataset/paribasa 27-3-25.xlsx")

# Streamlit UI
st.title("Chatbot Bahasa Sunda Loma")
st.write("Selamat datang! Silakan ajukan pertanyaan dalam bahasa Sunda.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Tulis pesan Anda:")

if st.button("Kirim") and user_input:
    bot_response = generate_text(user_input, pipe)
    text_constraint, kata_terdapat, kata_tidak_terdapat, pasangan_kata = highlight_text(
        bot_response, df_kamus
    )
    st.session_state.chat_history.append((user_input, text_constraint))

# Menampilkan riwayat chat
for user_msg, bot_msg in st.session_state.chat_history:
    st.markdown(f"**User:** {user_msg}", unsafe_allow_html=True)
    st.markdown(f"**Bot:** {bot_msg}", unsafe_allow_html=True)
