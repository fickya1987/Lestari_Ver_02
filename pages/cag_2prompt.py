import os
import openai
import pandas as pd
import streamlit as st
import re
import numpy as np
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

openai.api_key = os.getenv("OPENAI_API_KEY")

# Path setup
kamus_path = Path("dataset/data_kamus 27-3-25.xlsx")
embedding_path = Path("vector_data/embeddings_tfidf.pkl")
vectorizer_path = Path("vector_data/tfidf_vectorizer.pkl")

# Load kamus
df_kamus = pd.read_excel(kamus_path)
df_kamus.fillna("", inplace=True)

loma_values = {"LOMA", "Loma", "loma", "L", "LOMA/HALUS", "LOMA/KASAR", "HALUS/LOMA"}

# Vectorization with TF-IDF using enriched fields
kamus_corpus = (
    df_kamus["LEMA"].fillna("") + ", " +
    df_kamus["SUBLEMA"].fillna("") + ", " +
    df_kamus["ARTI"].fillna("") + ", " +
    df_kamus["SINONIM"].fillna("") + ", " +
    df_kamus["CONTOH KALIMAT LOMA"].fillna("") + ", " +
    df_kamus["(HALUS/LOMA/KASAR)"].fillna("")
)

if embedding_path.exists() and vectorizer_path.exists():
    with open(embedding_path, "rb") as f:
        kamus_embeddings = pickle.load(f)
    with open(vectorizer_path, "rb") as f:
        vectorizer = pickle.load(f)
else:
    vectorizer = TfidfVectorizer()
    kamus_embeddings = vectorizer.fit_transform(kamus_corpus)
    embedding_path.parent.mkdir(parents=True, exist_ok=True)
    with open(embedding_path, "wb") as f:
        pickle.dump(kamus_embeddings, f)
    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)

# Semantic search function
# Perbaikan fungsi semantic_search
def semantic_search(query, top_k=5):
    try:
        # Transform query to TF-IDF vector
        query_vec = vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarity_scores = cosine_similarity(query_vec, kamus_embeddings).flatten()
        
        # Get top-k results with highest similarity
        top_indices = similarity_scores.argsort()[-top_k:][::-1]
        top_scores = similarity_scores[top_indices]
        
        return df_kamus.iloc[top_indices], top_scores
    except Exception as e:
        st.error(f"Error in semantic search: {str(e)}")
        return pd.DataFrame(), np.array([])

# Perbaikan fungsi tampilkan_hasil_similarity
def tampilkan_hasil_similarity(hasil_df, scores):
    if hasil_df.empty:
        return "Tidak ditemukan hasil yang relevan"
    
    hasil_list = []
    for i, (idx, row) in enumerate(hasil_df.iterrows()):
        # Format score dengan presisi 4 digit
        formatted_score = f"{scores[i]:.4f}" if scores[i] > 0.0001 else "<0.0001"
        
        hasil_list.append(
            f"{i+1}. LEMA: {row['LEMA']}\n"
            f"   SUBLEMA: {row['SUBLEMA']}\n"
            f"   ARTI: {row['ARTI'][:100]}...\n"
            f"   GAYA: {row['(HALUS/LOMA/KASAR)']}\n"
            f"   Score: {formatted_score}\n"
            f"   {'='*50}"
        )
    return "\n\n".join(hasil_list)

# Fungsi bantu dasar
def pisah_kata(text):
    return re.findall(r"(\w+|[^\w\s])", text)

def cari_arti_kamus(token):
    match = df_kamus[df_kamus["LEMA"].str.lower() == token.lower()]
    if not match.empty:
        return match.iloc[0]["ARTI"]
    match = df_kamus[df_kamus["SUBLEMA"].str.lower() == token.lower()]
    if not match.empty:
        return match.iloc[0]["ARTI"]
    return token

# Translate Sunda ke Indonesia
def translate_sunda_to_indo(text):
    tokens = pisah_kata(text)
    hasil = [cari_arti_kamus(token) for token in tokens]
    return re.sub(r"\s+([^\w\s])", r"\1", " ".join(hasil))

# Translate Indonesia ke Sunda LOMA

def translate_indo_to_sunda(text):
    prompt = f"Terjemahkan kalimat berikut ke dalam Bahasa Sunda dengan gaya LOMA. Gunakan istilah yang sesuai dari kamus: \n{text}"

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Anda adalah penerjemah bahasa Indonesia ke Sunda LOMA yang akurat dan sopan. Anda orangnya to the point cuma melaksanakan tugas menterjemahkan Bahasa Indonesia ke Sunda LOMA."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

# Chatbot Hybrid
def chatbot_hybrid(prompt_sunda):
    sunda_to_indo = translate_sunda_to_indo(prompt_sunda)
    hasil_df, scores = semantic_search(sunda_to_indo)
    context = tampilkan_hasil_similarity(hasil_df, scores)
    lema_sublema = ", ".join(set(df_kamus["LEMA"].tolist() + df_kamus["SUBLEMA"].tolist()))

    # Step 1: LLM response in Indonesian
    template_prompt_indo = (
        f"Berikut adalah beberapa informasi kamus untuk membantu menjawab:\n{context}\n\n"
        f"Pertanyaan: {sunda_to_indo}\n"
        f"Gunakan kosakata dari kamus ini.: {lema_sublema}\n"
        f"Jawablah pertanyaan berikut dengan sopan dan menggunakan gaya bahasa Indonesia bagaikan dengan teman."
    )

    response_indo = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Kamu adalah assistant saya sekaligus sahabat dekat saya. Jangan gunakan embel-embel seperti robot atau seperti informan, anda layaknya manusia."},
            {"role": "user", "content": template_prompt_indo},
        ]
    )
    llm_output_indo = response_indo.choices[0].message.content

    # Step 2: Translate Indonesian to Sunda LOMA by LLM
    template_prompt_sunda = (
        f"Tuliskan hasil dalam Bahasa Indonesia ini dalam gaya bahasa Sunda LOMA. Anda dapat menggunakan kosakata dari kamus ini.:\n\n"
        f"{context}\n\n"
        f"Kalimat dalam bahasa Indonesia:\n{llm_output_indo}"
    )

    response_sunda = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Anda adalah asisten dan sahabat baik saya yang menulis dalam bahasa Sunda LOMA."},
            {"role": "user", "content": template_prompt_sunda},
        ]
    )

    final_output = response_sunda.choices[0].message.content

    return {
        "input_sunda": prompt_sunda,
        "translated_indo": sunda_to_indo,
        "context": context,
        "llm_output": llm_output_indo,
        "output_sunda": final_output
    }

# Streamlit UI
st.set_page_config(page_title="Chatbot Sunda-Indonesia", layout="centered")
st.title("🤖 Sunda-Indonesia Hybrid Chatbot")

menu = st.sidebar.selectbox("Pilih Fitur", ["Chatbot", "Sunda → Indonesia", "Indonesia → Sunda LOMA"])

if menu == "Chatbot":
    user_input = st.text_area("Masukkan teks dalam Bahasa Sunda:", height=100)
    if st.button("Jalankan Chatbot"):
        hasil = chatbot_hybrid(user_input)
        st.subheader("Output")
        st.write("🧠 Terjemahan ke Bahasa Indonesia:")
        st.success(hasil["translated_indo"])
        #st.write("📚 Konteks Kamus (TF-IDF Search):")
        #st.info(hasil["context"])
        st.write("🤖 Respon LLM (Bahasa Indonesia):")
        st.success(hasil["llm_output"])
        st.write("🌍 Output Final dalam Bahasa Sunda (LOMA):")
        st.success(hasil["output_sunda"])

elif menu == "Sunda → Indonesia":
    user_input = st.text_area("Masukkan teks Bahasa Sunda:", height=100)
    if st.button("Terjemahkan"):
        hasil = translate_sunda_to_indo(user_input)
        st.subheader("Hasil Terjemahan:")
        st.success(hasil)

elif menu == "Indonesia → Sunda LOMA":
    user_input = st.text_area("Masukkan teks Bahasa Indonesia:", height=100)
    if st.button("Terjemahkan"):
        hasil = translate_indo_to_sunda(user_input)
        st.subheader("Hasil Terjemahan:")
        st.success(hasil)
