# === translate_sunda_indo.py ===
import streamlit as st
from constraint2 import process_and_translate
from AI_sunda_indo import generate_text
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
st.title("Translate+Constraint Sunda - Indo")
st.write("Flowchart:")

image = Image.open("images/flowsundaindo.png")
max_width = 700
aspect_ratio = image.height / image.width
new_height = int(max_width * aspect_ratio)
image_resized = image.resize((max_width, new_height))

st.image(image_resized, use_container_width=False)

# Load the xlsx file
df_kamus = pd.read_excel("dataset/data_kamus 27-3-25.xlsx")
df_idiom = pd.read_excel("dataset/idiom 27-3-25.xlsx")
df_paribasa = pd.read_excel("dataset/paribasa 27-3-25.xlsx")

with st.expander("Contoh Input", expanded=False):
    st.write("Berikut beberapa contoh input yang bisa digunakan:")
    st.code("Anjeun parantos tuang? Mangga seueur tutungangeun di bumi abdi, kedah dongkap nya?")
    st.code("Maneh ngahaleuang nembangkeun wawangsalan bari gawé ngaladenan salakina")
    st.code("Sabodo aing, kudu modar atawa hirup, sia mah moal paduli")

# Input teks utama
input_text = st.text_area("Masukkan teks di sini:", "")

st.write("Masukkan teks yang ingin di translate. (ctrl+enter untuk mengirim teks)")
st.write("Teks yang dimasukkan:", input_text)

input_text = input_text.lower()
input_text = input_text.replace("é", "e").replace("è", "e")

hasil_translate_kamus = process_and_translate(df_kamus, df_idiom, df_paribasa, input_text)
penyempurnaan_text = generate_text(hasil_translate_kamus)

if input_text:
    st.markdown("Hasil Translate Kamus:", unsafe_allow_html=True)
    st.markdown(hasil_translate_kamus, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("Hasil Penyempurnaan AI:", unsafe_allow_html=True)
    st.markdown(penyempurnaan_text, unsafe_allow_html=True)
