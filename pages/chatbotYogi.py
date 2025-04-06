# ========== chatbotYogi.py ==========
import os
import openai
import pandas as pd
import streamlit as st
import re

openai.api_key = os.getenv("OPENAI_API_KEY")

# Load kamus
kamus_df = pd.read_excel("dataset/data_kamus 27-3-25.xlsx")

def pisahkan_tanda_baca(text):
    return re.findall(r"(\w+|[^\w\s])", text)

def constraint_sunda_to_indo(text):
    tokens = pisahkan_tanda_baca(text)
    translated_tokens = []
    for token in tokens:
        if token.isalpha():
            match = kamus_df[kamus_df["LEMA"].str.lower() == token.lower()]
            if not match.empty:
                translated_tokens.append(match["ARTI"].values[0])
                continue
            match = kamus_df[kamus_df["SUBLEMA"].str.lower() == token.lower()]
            if not match.empty:
                translated_tokens.append(match["ARTI"].values[0])
                continue
        translated_tokens.append(token)
    return re.sub(r"\s+([^\w\s])", r"\1", " ".join(translated_tokens))

def constraint_indo_to_sunda(text):
    tokens = pisahkan_tanda_baca(text)
    translated_tokens = []
    loma_values = {"LOMA", "Loma", "loma", "L", "LOMA/HALUS", "LOMA/KASAR", "HALUS/LOMA"}
    for token in tokens:
        if token.isalpha():
            match = kamus_df[(kamus_df["ARTI"].str.lower() == token.lower()) & (kamus_df["(HALUS/LOMA/KASAR)"].isin(loma_values))]
            if not match.empty:
                if pd.notna(match["LEMA"].values[0]):
                    translated_tokens.append(match["LEMA"].values[0])
                    continue
                elif pd.notna(match["SUBLEMA"].values[0]):
                    translated_tokens.append(match["SUBLEMA"].values[0])
                    continue
            sinonim_match = kamus_df[(kamus_df["SINONIM"].str.contains(token, na=False, case=False)) & (kamus_df["(HALUS/LOMA/KASAR)"].isin(loma_values))]
            if not sinonim_match.empty:
                if pd.notna(sinonim_match["LEMA"].values[0]):
                    translated_tokens.append(sinonim_match["LEMA"].values[0])
                    continue
                elif pd.notna(sinonim_match["SUBLEMA"].values[0]):
                    translated_tokens.append(sinonim_match["SUBLEMA"].values[0])
                    continue
        translated_tokens.append(token)
    return re.sub(r"\s+([^\w\s])", r"\1", " ".join(translated_tokens))

def get_llm_response(input_user):
    template_prompt = (
        "Mulai sekarang, kamu adalah teman bicara saya yang ramah, responsif, dan selalu antusias."
        " Kamu berbicara dalam bahasa Indonesia dengan gaya santai namun sopan dan menghormati norma."
        f" {input_user}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": template_prompt},
        ]
    )
    return response.choices[0].message.content

def chatbot(prompt):
    indo = constraint_sunda_to_indo(prompt)
    llm = get_llm_response(indo)
    back_to_sunda = constraint_indo_to_sunda(llm)
    return indo, llm, back_to_sunda

st.set_page_config(page_title="Chatbot Sunda-Indonesia", layout="centered")
st.markdown("""
<style>
body {background-color: #f8f9fa;}
.stTextArea textarea {font-size: 18px !important;}
.chat-container {border-radius: 10px; padding: 15px; background: #fff; box-shadow: 0px 2px 10px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Chatbot Sunda-Indonesia")
st.write("Masukkan teks dalam Bahasa Sunda, dan chatbot akan menjawab dengan cara yang sesuai!")

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
