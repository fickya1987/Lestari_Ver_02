import pandas as pd
import re
from AI_sunda_indo import ai_translate_fn

def process_and_translate(df_kamus, df_idiom, df_paribasa, text, ai_translate_fn):
    # Normalisasi data
    df_kamus["(HALUS/LOMA/KASAR)"] = df_kamus["(HALUS/LOMA/KASAR)"].str.strip()
    df_idiom["KLASIFIKASI (HALUS/LOMA/KASAR)"] = df_idiom["KLASIFIKASI (HALUS/LOMA/KASAR)"].str.strip()
    df_paribasa["KLASIFIKASI (HALUS/LOMA/KASAR)"] = df_paribasa["KLASIFIKASI (HALUS/LOMA/KASAR)"].str.strip()

    # Normalisasi karakter khusus
    df_kamus.loc[:, "LEMA"] = df_kamus["LEMA"].str.replace("[éÉèÈ]", "e", regex=True)

    # Gabungkan LEMA dan SUBLEMA
    df_kamus["SUBLEMA"].fillna("", inplace=True)
    df_kamus["combined_lema"] = (df_kamus["LEMA"].str.lower() + "," + df_kamus["SUBLEMA"].str.lower())
    df_kamus["combined_lema"] = df_kamus["combined_lema"].apply(lambda x: x.split(",") if isinstance(x, str) else [])

    # Buat kamus referensi
    kamus_dict = {
        word.strip(): row["ARTI"]
        for _, row in df_kamus.iterrows()
        for word in row["combined_lema"]
        if word.strip()
    }
    
    idiom_dict = {
        idiom.lower(): arti
        for idiom, arti in zip(df_idiom["IDIOM"], df_idiom["ARTI BAHASA INDONESIA"])
        if pd.notna(arti)
    }
    
    paribasa_dict = {
        paribasa.lower(): arti
        for paribasa, arti in zip(df_paribasa["PARIBASA"], df_paribasa["ARTI BAHASA INDONESIA"])
        if pd.notna(arti)
    }

    def translate_constraint(text):
        """Fungsi terjemahan tanpa spell checker"""
        words = re.findall(r"\b\w+\b|[.,!?;]", text)
        translated_words = []
        unresolved_words = []
        
        i = 0
        while i < len(words):
            found = False
            # Cek frasa dari panjang ke pendek (4 kata -> 3 kata -> 2 kata -> 1 kata)
            for n in range(4, 0, -1):
                if i + n <= len(words):
                    phrase = " ".join(words[i:i + n]).lower()
                    
                    # Prioritas: Idiom -> Paribasa -> Kamus
                    if phrase in idiom_dict:
                        translated_words.append(idiom_dict[phrase])
                        i += n
                        found = True
                        break
                    elif phrase in paribasa_dict:
                        translated_words.append(paribasa_dict[phrase])
                        i += n
                        found = True
                        break
                    elif n == 1:
                        word = phrase
                        if word in kamus_dict:
                            translated_words.append(kamus_dict[word])
                        else:
                            translated_words.append(word)  # Biarkan kata asli tanpa koreksi
                            unresolved_words.append(word)  # Catat kata yang tidak dikenal
                        i += 1
                        found = True
                        break
            if not found:
                i += 1

        # Format kalimat hasil terjemahan
        sentence_kamus = " ".join(translated_words)
        sentence_kamus = sentence_kamus.capitalize()
        sentence_kamus = re.sub(r'(\.|\!|\?)\s+(\w)', lambda m: m.group(0).upper(), sentence_kamus)

        # Serahkan ke AI untuk penanganan typo dan penyempurnaan
        sentence_ai = ai_translate_fn(text, unresolved_words)

        return sentence_kamus, unresolved_words

    return translate_constraint(text)
