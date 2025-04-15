# === translate_sunda_indo.py ===
import streamlit as st
from constraint2 import process_and_translate
from AI_sunda_indo import generate_text, ai_translate_fn
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

image = Image.open("images/flowsundaindo_update.png")
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

#st.write("Masukkan teks yang ingin di translate. (ctrl+enter untuk mengirim teks)")
st.write("Teks yang dimasukkan:", input_text)

input_text = input_text.lower()
input_text = input_text.replace("é", "e").replace("è", "e")

#hasil_translate_kamus, hasil_ai = process_and_translate(df_kamus, df_idiom, df_paribasa, input_text, ai_translate_fn)
#penyempurnaan_text = generate_text(hasil_ai)

if st.button("🔍 Terjemahkan & Chat"):
    if input_text.strip():
        with st.spinner("Menghasilkan respon..."):
            hasil_translate_kamus, unknown_words = process_and_translate(df_kamus, df_idiom, df_paribasa, input_text, ai_translate_fn)
            hasil_ai = ai_translate_fn(hasil_translate_kamus, unknown_words)
            penyempurnaan_text = generate_text(hasil_ai)
        st.markdown("### 🔤 Hasil Terjemahan Kamus")
        st.markdown(f"""<div style="background-color:#2C2C3A;padding:15px;border-radius:10px;margin-bottom:15px;">
        <p style="font-size:16px;color:white;">{hasil_translate_kamus}</p></div>""", unsafe_allow_html=True)
        st.markdown("### 🤖 Koreksi oleh AI")
        st.markdown(f"""<div style="background-color:#3E3E50;padding:15px;border-radius:10px;margin-bottom:15px;">
        <p style="font-size:16px;color:white;">{hasil_ai}</p></div>""", unsafe_allow_html=True)
        st.markdown("### 🌟 Versi Akhir yang Lebih Natural")
        st.markdown(f"""<div style="background-color:#4CAF50;padding:15px;border-radius:10px;">
        <p style="font-size:16px;color:white;">{penyempurnaan_text}</p></div>""", unsafe_allow_html=True)
    else:
        st.warning("Silakan masukkan teks sebelum mengklik tombol!")


