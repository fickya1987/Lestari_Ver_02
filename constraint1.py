import random
import re
import pandas as pd
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

from huggingface_hub import login
import os
from dotenv import load_dotenv

load_dotenv()
login(token=os.getenv("HUGGINGFACE_TOKEN"))



# def merge_ner_results(results):
#     """
#     Fungsi untuk menggabungkan hasil Named Entity Recognition (NER) yang memiliki subkata.

#     Args:
#         results (list of dict): List hasil NER dari classifier.

#     Returns:
#         list: List entitas yang telah digabung.
#         list: List kata unik dari entitas yang telah digabung.
#     """
#     merged_entities = []
#     current_entity = {"word": "", "entity": None, "score": []}

#     for item in results:
#         word = item["word"]
#         entity = item["entity"]
#         score = item["score"]

#         if word.startswith("▁"):  # Awal kata baru
#             if current_entity["word"]:  # Simpan entitas sebelumnya
#                 current_entity["score"] = sum(current_entity["score"]) / len(
#                     current_entity["score"]
#                 )
#                 merged_entities.append(current_entity)
#             current_entity = {
#                 "word": word.replace("▁", ""),
#                 "entity": entity,
#                 "score": [score],
#             }
#         else:
#             current_entity["word"] += word  # Gabungkan subkata
#             current_entity["score"].append(score)

#     if current_entity["word"]:
#         current_entity["score"] = sum(current_entity["score"]) / len(
#             current_entity["score"]
#         )
#         merged_entities.append(current_entity)

#     unique_words = list(set(entity["word"] for entity in merged_entities))

#     return merged_entities, unique_words


def constraint_text(text, df_kamus):
    # tokenizer = AutoTokenizer.from_pretrained(
    #     "xlm-roberta-large-finetuned-conll03-english"
    # )
    # model = AutoModelForTokenClassification.from_pretrained(
    #     "xlm-roberta-large-finetuned-conll03-english"
    # )
    # classifier = pipeline("ner", model=model, tokenizer=tokenizer)

    # ================= Clean text_kecil =================
    text = text.replace("-", " ")
    text_kecil_clean = re.sub(r"[^\w\s-]", "", text.lower())

    # ================= Filter Kata di Kamus =================

    # results = classifier(text)
    # merged_entities, unique_words = merge_ner_results(results)
    # # for entity in merged_entities:
    # #     print(f"Entitas: {entity['word']}, Label: {entity['entity']}, Score: {entity['score']:.4f}")
    # nama_orang_tempat = set(unique_words)
    # nama_orang_tempat = set(item.lower() for item in nama_orang_tempat)
    # print(f"nama_orang_tempat : {nama_orang_tempat}")

    df_e_petik = df_kamus[df_kamus["LEMA"].str.contains("[éÉ]", na=False, regex=True)]
    df_e_petik.loc[:, "LEMA"] = df_e_petik["LEMA"].str.replace("[éÉ]", "e", regex=True)
    kata_e_petik = {kata.lower() for kata in df_e_petik["LEMA"].astype(str)}

    df_e_petik2 = df_kamus[df_kamus["LEMA"].str.contains("[èÈ]", na=False, regex=True)]
    df_e_petik2.loc[:, "LEMA"] = df_e_petik2["LEMA"].str.replace(
        "[èÈ]", "e", regex=True
    )
    kata_e_petik2 = {kata.lower() for kata in df_e_petik2["LEMA"].astype(str)}

    kata_kalimat = set(text_kecil_clean.split())
    kata_dataframe1 = {
        kata.lower() for kata in df_kamus["LEMA"].astype(str)
    }  # Konversi ke string jika ada NaN

    kata_dataframe2 = {
        kata.strip().replace(".", "")  # Hapus spasi ekstra & titik
        for kata_list in df_kamus["SUBLEMA"].astype(str)  # Konversi ke string
        for kata in kata_list.split(",")  # Pecah berdasarkan koma
        if kata.strip()  # Hanya tambahkan jika tidak kosong
    }

    # Membersihkan teks: Menghapus tanda baca dan membuat huruf kecil
    def clean_text(text):
        text = re.sub(r"[^\w\s]", "", text)  # Hapus tanda baca
        return text.lower()  # Konversi ke huruf kecil

    kata_dataframe3 = {
        kata.strip().replace(".", "")  # Hapus spasi ekstra & titik
        for kata_list in df_kamus["SINONIM"].astype(str)  # Konversi ke string
        for kata in kata_list.split(",")  # Pecah berdasarkan koma
        if kata.strip()  # Hanya tambahkan jika tidak kosong
    }

    # Memisahkan setiap kata dalam set
    kata_dataframe4 = {
        kata
        for kalimat in df_kamus["CONTOH KALIMAT LOMA"].astype(str)
        for kata in clean_text(kalimat).split()
    }

    # kata_dataframe = kata_dataframe1 | kata_dataframe2 | kata_dataframe4

    kata_dataframe = (
        kata_dataframe1
        | kata_dataframe2
        | kata_dataframe3
        | kata_dataframe4
        | kata_e_petik
        | kata_e_petik2
        # | nama_orang_tempat
    )

    kata_terdapat = sorted(kata_kalimat.intersection(kata_dataframe))
    kata_terdapat = [kata for kata in kata_terdapat if not re.search(r"\d", kata)]

    kata_tidak_terdapat = sorted(kata_kalimat - kata_dataframe)
    kata_tidak_terdapat = [
        kata for kata in kata_tidak_terdapat if not re.search(r"\d", kata)
    ]

    print("\n")
    print("Kata yang ditemukan di Kamus:", kata_terdapat)
    print("Kata yang tidak ditemukan di Kamus:", kata_tidak_terdapat)

    # =====================================================================================
    # ======================== 9. Apakah ada sinonim Berjenis Loma? ========================
    # =====================================================================================

    # Dictionary untuk menyimpan pasangan kata asli dan kata pengganti
    pasangan_kata = {}
    kata_terdapat_tidak_loma = []

    # Loop setiap kata dalam kata_terdapat
    for kata in kata_terdapat[
        :
    ]:  # Gunakan slicing agar bisa mengubah list di dalam loop
        # Cari kata di kamus
        row = df_kamus[df_kamus["LEMA"].str.lower() == kata]

        if not row.empty:
            kategori = row["(HALUS/LOMA/KASAR)"].values[0]  # Ambil kategori kata utama

            if pd.notna(kategori) and "LOMA" not in kategori.upper():
                # Ambil daftar sinonim dari kolom SINONIM
                sinonim_raw = (
                    row["SINONIM"].values[0]
                    if pd.notna(row["SINONIM"].values[0])
                    else ""
                )
                sinonim_list = [s.strip() for s in sinonim_raw.split(",") if s.strip()]

                # Cari sinonim yang berkategori "LOMA"
                sinonim_loma = []
                for sinonim in sinonim_list:
                    sinonim_row = df_kamus[df_kamus["LEMA"].str.lower() == sinonim]
                    if not sinonim_row.empty:
                        kategori_sinonim = sinonim_row["(HALUS/LOMA/KASAR)"].values[0]
                        if kategori_sinonim == "LOMA":
                            sinonim_loma.append(sinonim)

                # Jika ada sinonim LOMA, pilih salah satu sebagai pengganti
                if sinonim_loma:
                    pasangan_kata[kata] = random.choice(sinonim_loma)
                else:
                    # Jika tidak ada sinonim LOMA, pindahkan ke kata_tidak_terdapat
                    kata_tidak_terdapat.append(kata)
                    kata_terdapat.remove(kata)  # Hapus dari kata_terdapat
                    kata_terdapat_tidak_loma.append(kata)

    # Tampilkan hasil pasangan kata
    for kata_asli, kata_pengganti in pasangan_kata.items():
        kata_terdapat.append(kata_pengganti)
        print(f"{kata_asli} -> {kata_pengganti}")

    print(pasangan_kata)

    return (
        kata_terdapat,
        kata_tidak_terdapat,
        kata_terdapat_tidak_loma,
        pasangan_kata,
        kata_e_petik,
        kata_e_petik2,
    )


def highlight_text(translated_text, df_kamus):
    (
        kata_terdapat,
        kata_tidak_terdapat,
        kata_terdapat_tidak_loma,
        pasangan_kata,
        kata_e_petik,
        kata_e_petik2,
    ) = constraint_text(translated_text, df_kamus)

    hasil_lines = []

    for baris in translated_text.splitlines():
        kata_list = baris.split()
        hasil_baris = []

        i = 0
        while i < len(kata_list):
            match = re.match(r"([\w'-]+)(\W*)", kata_list[i])
            if not match:
                matches = re.findall(r"\*([^\s*]+)\*", translated_text)
                if matches:
                    kata_list_clean = re.sub(r"[^a-zA-Z0-9\s]", "", kata_list[i])
                    if kata_list_clean not in kata_terdapat:
                        hasil_baris.append(
                            f'<span style="color:blue; font-style:italic;">{kata_list[i]}</span>'
                        )
                    else:
                        hasil_baris.append(kata_list[i])
                else:
                    hasil_baris.append(kata_list[i])
                i += 1
                continue

            kata, simbol = match.groups()
            kata = pasangan_kata.get(kata, kata)

            if kata.lower() not in kata_terdapat:
                if kata.lower() not in kata_terdapat_tidak_loma:
                    if re.search(r"\d", kata):
                        hasil_baris.append(kata + simbol)
                    else:
                        hasil_baris.append(
                            f'<span style="color:red; font-style:italic;">{kata}</span>{simbol}'
                        )
                else:
                    hasil_baris.append(
                        f'<span style="color:purple; font-style:italic;">{kata}</span>{simbol}'
                    )
            else:
                kata_lower = kata.lower()
                if kata_lower in kata_e_petik:
                    kata = kata.replace("e", "é").replace("E", "É")
                if kata_lower in kata_e_petik2:
                    kata = kata.replace("e", "è").replace("E", "È")
                hasil_baris.append(kata + simbol)

            i += 1
        hasil_lines.append(" ".join(hasil_baris))

    return "<br>".join(hasil_lines), kata_terdapat, kata_tidak_terdapat, pasangan_kata
