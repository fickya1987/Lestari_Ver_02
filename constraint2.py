import pandas as pd
import re


def process_and_translate(df_kamus, df_idiom, df_paribasa, text):
    """
    Normalisasi data, membangun kamus dari tiga dataframe (kamus, idiom, paribasa),
    dan menerjemahkan teks dengan constraint berdasarkan kamus yang telah dibuat.
    """
    # Normalisasi kategori bahasa
    df_kamus["(HALUS/LOMA/KASAR)"] = df_kamus["(HALUS/LOMA/KASAR)"].str.strip()
    df_idiom["KLASIFIKASI (HALUS/LOMA/KASAR)"] = df_idiom[
        "KLASIFIKASI (HALUS/LOMA/KASAR)"
    ].str.strip()
    df_paribasa["KLASIFIKASI (HALUS/LOMA/KASAR)"] = df_paribasa[
        "KLASIFIKASI (HALUS/LOMA/KASAR)"
    ].str.strip()

    # SOLVE PROBLEM e aksen
    df_kamus.loc[:, "LEMA"] = df_kamus["LEMA"].str.replace("[éÉ]", "e", regex=True)
    df_kamus.loc[:, "LEMA"] = df_kamus["LEMA"].str.replace("[èÈ]", "e", regex=True)

    # Gabungkan LEMA dan SUBLEMA ke dalam satu set kata kunci
    df_kamus["SUBLEMA"].fillna("", inplace=True)
    df_kamus["combined_lema"] = (
        df_kamus["LEMA"].str.lower() + "," + df_kamus["SUBLEMA"].str.lower()
    )
    df_kamus["combined_lema"] = df_kamus["combined_lema"].apply(
        lambda x: x.split(",") if isinstance(x, str) else []
    )

    # Bangun kamus
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
        for paribasa, arti in zip(
            df_paribasa["PARIBASA"], df_paribasa["ARTI BAHASA INDONESIA"]
        )
        if pd.notna(arti)
    }

    # Fungsi penerjemahan
    def translate_constraint(text):
        words = re.findall(r"\b\w+\b|[.,!?;]", text)
        translated_words = []
        i = 0
        while i < len(words):
            phrase = " ".join(words[i : i + 2]).lower()
            if phrase in idiom_dict:
                translated_words.append(idiom_dict[phrase])
                i += 2
                continue
            elif phrase in paribasa_dict:
                translated_words.append(paribasa_dict[phrase])
                i += 2
                continue

            word = words[i].lower()
            translated_words.append(kamus_dict.get(word, word))
            i += 1

        return " ".join(translated_words)

    return translate_constraint(text)
