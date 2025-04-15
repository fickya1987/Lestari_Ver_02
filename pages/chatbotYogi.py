# ========== chatbotYogi.py ==========
import os
import openai
import pandas as pd
import streamlit as st
import re
from constraint1 import highlight_text

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'last_response' not in st.session_state:
    st.session_state.last_response = None

openai.api_key = os.getenv("OPENAI_API_KEY")

# Load kamus
kamus_df = pd.read_excel("dataset/data_kamus 27-3-25.xlsx")

loma_values = {"LOMA", "Loma", "loma", "L", "LOMA/HALUS", "LOMA/KASAR", "HALUS/LOMA"}

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

# def sunda_ai_to_sunda_loma(text):
#     tokens = pisahkan_tanda_baca(text)
#     translated_tokens = []
#     for token in tokens:
#         if token.isalpha():
#             token_lower = token.lower()
#             match = kamus_df[(kamus_df["LEMA"].str.lower() == token_lower) | (kamus_df["SUBLEMA"].str.lower() == token_lower)]
#             if not match.empty:
#                 loma_match = match[kamus_df["(HALUS/LOMA/KASAR)"].isin(loma_values)]
#                 if not loma_match.empty:
#                     translated_tokens.append(token_lower)
#                 else:
#                     sinonim_series = match["SINONIM"].dropna()
#                     kandidat = []
#                     for sinonim_str in sinonim_series:
#                         kandidat += [s.strip().lower() for s in sinonim_str.split(",") if s.strip()]
#                     found = False
#                     for k in kandidat:
#                         alt_match = kamus_df[((kamus_df["LEMA"].str.lower() == k) | (kamus_df["SUBLEMA"].str.lower() == k)) & kamus_df["(HALUS/LOMA/KASAR)"].isin(loma_values)]
#                         if not alt_match.empty:
#                             translated_tokens.append(k)
#                             found = True
#                             break
#                     if not found:
#                         translated_tokens.append(f"*{token_lower}*")
#             else:
#                 translated_tokens.append(f"*{token_lower}*")
#         else:
#             translated_tokens.append(token)

#     kalimat = " ".join(translated_tokens)
#     kalimat = re.sub(r"\s+([^\w\s])", r"\1", kalimat)
#     kalimat = re.sub(r"([.!?]\s*)(\w)", lambda m: m.group(1) + m.group(2).upper(), kalimat.capitalize())
#     return kalimat

def get_llm_response(input_user):
    # Include conversation history in the prompt
    history_context = "\n".join([f"{'User' if i%2==0 else 'Assistant'}: {msg}" 
                               for i, msg in enumerate(st.session_state.conversation_history[-4:])])

    template_prompt = (
        "Mulai sekarang, kamu adalah teman bicara saya yang ramah, responsif, dan selalu antusias. Kamu berbicara dalam bahasa Indonesia dengan gaya santai namun sopan dan menghormati norma."
        f" {input_user}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": template_prompt},
        ]
    )
    return response.choices[0].message.content

def translate_with_llm(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Terjemahkan ke dalam bahasa Sunda"},
            {"role": "user", "content": text},
        ]
    )
    return response.choices[0].message.content

def chatbot(prompt):
    # Add user message to history
    st.session_state.conversation_history.append(f"User (Sunda): {prompt}")

    indo = constraint_sunda_to_indo(prompt)
    llm = get_llm_response(indo)
    sunda_ai = translate_with_llm(llm)
    sunda_loma, kata_terdapat, kata_tidak_terdapat, pasangan_kata = highlight_text(sunda_ai, kamus_df)
    # Add assistant response to history
    st.session_state.conversation_history.append(f"Assistant (Sunda): {sunda_loma}")
    
    # Store last response details
    st.session_state.last_response = {
        "constraint_prompt": indo,
        "llm_response": llm,
        "sunda_loma": sunda_loma
    }
    return indo, llm, sunda_ai, sunda_loma
   
# UI Setup
st.set_page_config(page_title="Chatbot Sunda-Indonesia", layout="centered")
st.markdown("""
<style>
body {background-color: #f8f9fa;}
.stTextArea textarea {font-size: 18px !important;}
.chat-container {border-radius: 10px; padding: 15px; background: #fff; box-shadow: 0px 2px 10px rgba(0,0,0,0.1);}
.chat-bubble-user {background-color: #e3f2fd; border-radius: 15px; padding: 10px; margin: 5px 0; max-width: 80%; float: right;}
.chat-bubble-bot {background-color: #f5f5f5; border-radius: 15px; padding: 10px; margin: 5px 0; max-width: 80%; float: left;}
.clear-history {margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Chatbot Sunda-Indonesia")
st.write("Masukkan teks dalam Bahasa Sunda, dan chatbot akan menjawab dengan cara yang sesuai!")

# Display conversation history
st.markdown("### 📜 Riwayat Percakapan")
if len(st.session_state.conversation_history) > 0:
    for i, message in enumerate(st.session_state.conversation_history):
        if "User" in message:
            st.markdown(f'<div class="chat-bubble-user"><b>Anda:</b> {message.split(": ")[1]}</div>', 
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-bot"><b>Bot:</b> {message.split(": ")[1]}</div>', 
                        unsafe_allow_html=True)
else:
    st.info("Belum ada percakapan. Mulailah mengobrol!")

# Input area with form for better control
with st.form("chat_form"):
    user_input = st.text_area("💬 Masukkan teks dalam Bahasa Sunda:", height=100, key="chat_input")
    
    col1, col2 = st.columns(2)
    with col1:
        submit_button = st.form_submit_button("🔍 Terjemahkan & Chat")
    with col2:
        clear_button = st.form_submit_button("🧹 Hapus Riwayat")

    if submit_button and user_input.strip():
        with st.spinner("Menghasilkan respon..."):
            constraint_prompt, llm_response, sunda_ai, sunda_loma = chatbot(user_input)
        st.rerun()
    
    if clear_button:
        st.session_state.conversation_history = []
        st.session_state.last_response = None
        st.rerun()

# Display current response details if available
if st.session_state.last_response:
    st.markdown("## 📝 Detail Respon Terakhir")
    st.write("**✅ Constraint Prompt (Sunda → Indo):**")
    st.success(st.session_state.last_response["constraint_prompt"])
    st.write("**🤖 Output LLM (Bahasa Indonesia):**")
    st.info(st.session_state.last_response["llm_response"])
    st.write("**🌍 Output Final (Sunda → LOMA):**")
    st.markdown(st.session_state.last_response["sunda_loma"], unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='color: red;'>Kata Kata yang Tidak ditemukan di Kamus</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: purple;'>Kata Kata yang ada di kamus namun Tidak ditemukan Loma</p>", unsafe_allow_html=True)
    #st.markdown(f"<p style='color: red;'>{st.session_state.last_response['kata_tidak_terdapat']}</p>", unsafe_allow_html=True)
