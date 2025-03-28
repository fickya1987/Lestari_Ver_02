import streamlit as st
from PIL import Image

# Konfigurasi halaman harus dipanggil pertama
st.set_page_config(page_title="Main Page", page_icon="📌", layout="wide")

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


def main():
    st.title("Selamat Datang di Lestari2 Beta")
    st.write("Ini adalah halaman utama dari aplikasi Lestari2 Beta sederhana.")
    st.write("Ada 4 fitur yaitu:")

    st.write("1. Translasi Indonesia ke sunda")

    st.write("2. Translasi Sunda ke Indonesia")

    st.write("3. Chatbot Syahmi")
    st.write(
        "User input bahasa sunda -> menyuruh Gemma3 menjawab dengan bahasa sunda -> melakukan constraint untuk memfilter bahasa bukan loma -> selesai"
    )

    st.write("4. Chatbot Yogi")
    st.write(
        "User input bahasa sunda -> constraint diubah menjadi bahasa indonesia -> menyuruh Gemma3 menjawab dengan bahasa indonesia -> melakukan constraint untuk mengubah bahasa indonesia menjadi bahasa sunda -> selesai"
    )


if __name__ == "__main__":
    main()
