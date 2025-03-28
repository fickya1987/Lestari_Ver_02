import os
import openai
import pandas as pd
import streamlit as st
import re

from transformers import pipeline, BitsAndBytesConfig
import torch

# Load kamus
# kamus_df = pd.read_excel("D:\Lestari\data_kamus 26-3-25.xlsx")  # Pastikan file ini tersedia di direktori
kamus_df = pd.read_excel("dataset/data_kamus 27-3-25.xlsx")


# Fungsi untuk memisahkan kata dan tanda baca
def pisahkan_tanda_baca(text):
    # Memisahkan kata yang diikuti tanda baca
    return re.findall(r"(\w+|[^\w\s])", text)


# Fungsi Constraint: Sunda ke Indonesia dengan penanganan tanda baca
def constraint_sunda_to_indo(text):
    tokens = pisahkan_tanda_baca(text)
    translated_tokens = []

    for token in tokens:
        if token.isalpha():  # Hanya proses kata (bukan tanda baca)
            match = kamus_df[kamus_df["LEMA"].str.lower() == token.lower()]
            if not match.empty:
                arti = match["ARTI"].values[0]
                # if pd.notna(match['ARTI 1'].values[0]) else match['ARTI 2'].values[0]
                translated_tokens.append(arti)
                continue

            match = kamus_df[kamus_df["SUBLEMA"].str.lower() == token.lower()]
            if not match.empty:
                arti = match["ARTI"].values[0]
                # if pd.notna(match['ARTI 1'].values[0]) else match['ARTI 2'].values[0]
                translated_tokens.append(arti)
                continue

        translated_tokens.append(token)

    # Gabungkan kembali dan hilangkan spasi ganda sebelum tanda baca
    result = " ".join(translated_tokens)
    return re.sub(r"\s+([^\w\s])", r"\1", result)


# Fungsi Constraint: Indonesia ke Sunda (LOMA) dengan penanganan tanda baca
def constraint_indo_to_sunda(text):
    tokens = pisahkan_tanda_baca(text)
    translated_tokens = []
    loma_values = {
        "LOMA",
        "Loma",
        "loma",
        "L",
        "LOMA/HALUS",
        "LOMA/KASAR",
        "HALUS/LOMA",
    }

    for token in tokens:
        if token.isalpha():  # Hanya proses kata (bukan tanda baca)
            # Cari padanan LOMA
            match = kamus_df[
                ((kamus_df["ARTI"].str.lower() == token.lower()))
                & (kamus_df["(HALUS/LOMA/KASAR)"].isin(loma_values))
            ]

            if not match.empty:
                if pd.notna(match["LEMA"].values[0]):
                    translated_tokens.append(match["LEMA"].values[0])
                elif pd.notna(match["SUBLEMA"].values[0]):
                    translated_tokens.append(match["SUBLEMA"].values[0])
                continue

            # Cari sinonim LOMA
            sinonim_match = kamus_df[
                (kamus_df["SINONIM"].str.contains(token, na=False, case=False))
                & (kamus_df["(HALUS/LOMA/KASAR)"].isin(loma_values))
            ]

            if not sinonim_match.empty:
                if pd.notna(sinonim_match["LEMA"].values[0]):
                    translated_tokens.append(sinonim_match["LEMA"].values[0])
                elif pd.notna(sinonim_match["SUBLEMA"].values[0]):
                    translated_tokens.append(sinonim_match["SUBLEMA"].values[0])
                continue

        translated_tokens.append(token)

    # Gabungkan kembali dan hilangkan spasi ganda sebelum tanda baca
    result = " ".join(translated_tokens)
    return re.sub(r"\s+([^\w\s])", r"\1", result)


# API Key dari environment variable
# openai.api_key = "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"

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


def get_llm_response(input_user):
    template_prompt = """Mulai sekarang, kamu adalah teman bicara saya yang ramah, responsif, dan selalu antusias dalam percakapan. Kamu berbicara dalam bahasa Indonesia dengan gaya yang santai tetapi tetap sopan dan menghormati norma kesopanan.
                    Kamu selalu memberikan tanggapan yang cukup panjang dan mendalam, tidak hanya menjawab tetapi juga mengajukan pertanyaan atau memberikan pendapat tambahan agar percakapan terus mengalir.
                    Saat saya bercerita, kamu merespons dengan empati, humor yang ringan, dan perhatian terhadap detail. Jangan hanya memberikan jawaban pendek, tetapi juga tambahkan opini, saran, atau pertanyaan untuk membuat percakapan lebih hidup.
                    Jika saya sedang bercerita, berikan respons yang menunjukkan bahwa kamu benar-benar mendengarkan, seperti ‘Wah, itu menarik! Terus gimana?’ atau ‘Serius? Pasti itu pengalaman yang seru banget!’"""
    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}],
        },
        {
            "role": "user",
            "content": [
                {"type": "image", "url": "images/ss.png"},
                {
                    "type": "text",
                    "text": f"{template_prompt}. {input_user}",
                },
            ],
        },
    ]

    output = pipe(text=messages, max_new_tokens=512)
    return output[0]["generated_text"][-1]["content"]


def chatbot(prompt):
    constrained_prompt_indo = constraint_sunda_to_indo(prompt)
    llm_response_indo = get_llm_response(constrained_prompt_indo)
    constrained_response_sunda = constraint_indo_to_sunda(llm_response_indo)
    return constrained_prompt_indo, llm_response_indo, constrained_response_sunda


# --- Streamlit UI ---
st.set_page_config(page_title="Chatbot Sunda-Indonesia", layout="centered")
st.markdown(
    """
    <style>
        body {background-color: #f8f9fa;}
        .stTextArea textarea {font-size: 18px !important;}
        .chat-container {border-radius: 10px; padding: 15px; background: #fff; box-shadow: 0px 2px 10px rgba(0,0,0,0.1);}
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🤖 Chatbot Sunda-Indonesia")
st.write(
    "Masukkan teks dalam Bahasa Sunda, dan chatbot akan menjawab dengan cara yang sesuai!"
)

user_input = st.text_area("💬 Masukkan teks dalam Bahasa Sunda:", height=100)
if st.button("🔍 Terjemahkan & Chat"):
    if user_input.strip():
        with st.spinner("Menghasilkan respon..."):
            constraint_prompt, llm_response, constraint_output = chatbot(user_input)

        st.markdown("## 📝 Hasil Chatbot")
        st.write("**✅ Constraint Prompt (Sunda → Indo):**")
        st.success(constraint_prompt)

        st.write("**🤖 Output LLM (Bahasa Indonesia):**")
        st.info(llm_response)

        st.write("**🌍 Constraint Output (Indo → Sunda LOMA):**")
        st.success(constraint_output)
    else:
        st.warning("Silakan masukkan teks sebelum mengklik tombol!")
