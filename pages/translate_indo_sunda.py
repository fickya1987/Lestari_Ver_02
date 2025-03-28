import streamlit as st
from constraint1 import highlight_text
from AI_indo_sunda import generate_text
import pandas as pd
from PIL import Image
import re

from transformers import pipeline, BitsAndBytesConfig
import torch

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


# Streamlit UI
st.title("Translate+Constraint Indo - Sunda")
st.write("Flowchart:")

image = Image.open("images/flowindosunda.png")
# Resize gambar (misalnya lebar 300px, tinggi menyesuaikan)
max_width = 700
aspect_ratio = image.height / image.width
new_height = int(max_width * aspect_ratio)
image_resized = image.resize((max_width, new_height))

# Menampilkan gambar di tengah menggunakan HTML dan CSS
st.markdown(
    f"""
    <div style="display: flex; justify-content: center;">
        <img src="data:image/png;base64,{st.image(image_resized, output_format='PNG')}" width="{max_width}px"/>
    </div>
    """,
    unsafe_allow_html=True,
)

# Expander untuk menampilkan contoh input
with st.expander("Contoh Input", expanded=False):
    st.write("Berikut beberapa contoh input yang bisa digunakan:")
    st.code("Apa Kabar?")
    st.code("Saya pergi ke pasar pagi ini.")
    st.code("Mereka sedang berdiskusi tentang proyek baru.")

st.write("Masukkan teks yang ingin di translate.")
input_text = st.text_area("Masukkan teks di sini: (ctrl+enter untuk mengirim teks)", "")

if input_text != "":
    translated_text = generate_text(input_text, pipe)
    translated_text = translated_text.lower()
    # Load the xlsx file
    df_kamus = pd.read_excel("dataset/data_kamus 27-3-25.xlsx")
    df_kamus.head(50)

    highlighted_text, kata_terdapat, kata_tidak_terdapat, pasangan_kata = (
        highlight_text(translated_text, df_kamus)
    )

    st.markdown("Hasil Translate:", unsafe_allow_html=True)
    st.markdown(highlighted_text, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: yellow;'>INFORMASI TAMBAHAN</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color: yellow;'>Kata Kata yang diganti ke Loma:</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color: yellow;'>{pasangan_kata}</p>", unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: yellow;'>Kata Kata yang ditemukan di Kamus:</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color: yellow;'>{kata_terdapat}</p>", unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: yellow;'>Kata Kata yang Tidak ditemukan di Kamus:</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color: yellow;'>{kata_tidak_terdapat}</p>", unsafe_allow_html=True
    )
