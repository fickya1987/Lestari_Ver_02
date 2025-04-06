# === translate_indo_sunda.py ===
import streamlit as st
from constraint1 import highlight_text
from AI_indo_sunda import generate_text
import pandas as pd
from PIL import Image
import re

# Menambahkan CSS dengan beberapa opsi warna
st.markdown(
    """
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
    .content {
        color: white;
        font-size: 1em;
    }
    label {
        color: white !important;
    }
    input {
        color: white !important;
        background-color: black !important;
    }
    ::placeholder {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit UI
st.title("Translate+Constraint Indo - Sunda")
st.write("Flowchart:")

image = Image.open("images/flowindosunda.png")
max_width = 700
aspect_ratio = image.height / image.width
new_height = int(max_width * aspect_ratio)
image_resized = image.resize((max_width, new_height))

st.image(image_resized, use_container_width=False)

with st.expander("Contoh Input", expanded=False):
    st.write("Berikut beberapa contoh input yang bisa digunakan:")
    st.code("Apa Kabar?")
    st.code("Saya pergi ke pasar pagi ini.")
    st.code("Mereka sedang berdiskusi tentang proyek baru.")

st.write("Masukkan teks yang ingin di translate.")
input_text = st.text_area("Masukkan teks di sini: (ctrl+enter untuk mengirim teks)", "")

if input_text != "":
    translated_text = generate_text(input_text)
    translated_text = translated_text.lower()

    df_kamus = pd.read_excel("dataset/data_kamus 27-3-25.xlsx")
    highlighted_text, kata_terdapat, kata_tidak_terdapat, pasangan_kata = (
        highlight_text(translated_text, df_kamus)
    )

    st.markdown("Hasil Translate:", unsafe_allow_html=True)
    st.markdown(highlighted_text, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color: yellow;'>INFORMASI TAMBAHAN</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: yellow;'>Kata Kata yang diganti ke Loma:</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: yellow;'>{pasangan_kata}</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color: yellow;'>Kata Kata yang ditemukan di Kamus:</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: yellow;'>{kata_terdapat}</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color: yellow;'>Kata Kata yang Tidak ditemukan di Kamus:</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: yellow;'>{kata_tidak_terdapat}</p>", unsafe_allow_html=True)
