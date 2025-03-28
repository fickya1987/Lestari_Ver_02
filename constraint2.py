import pandas as pd
import re
from typing import Dict

def process_and_translate(
    df_kamus: pd.DataFrame,
    df_idiom: pd.DataFrame,
    df_paribasa: pd.DataFrame,
    text: str
) -> str:
    """Process and translate text using dictionaries."""
    # Normalize data
    df_kamus["(HALUS/LOMA/KASAR)"] = df_kamus["(HALUS/LOMA/KASAR)"].str.strip()
    df_idiom["KLASIFIKASI (HALUS/LOMA/KASAR)"] = df_idiom["KLASIFIKASI (HALUS/LOMA/KASAR)"].str.strip()
    
    # Clean special characters
    df_kamus["LEMA"] = df_kamus["LEMA"].str.replace("[éèÉÈ]", "e", regex=True)
    df_kamus["SUBLEMA"].fillna("", inplace=True)
    
    # Build dictionaries
    kamus_dict = build_kamus_dict(df_kamus)
    idiom_dict = build_phrase_dict(df_idiom, "IDIOM", "ARTI BAHASA INDONESIA")
    paribasa_dict = build_phrase_dict(df_paribasa, "PARIBASA", "ARTI BAHASA INDONESIA")
    
    return translate_text(text, kamus_dict, idiom_dict, paribasa_dict)

def build_kamus_dict(df: pd.DataFrame) -> Dict[str, str]:
    """Build dictionary from kamus dataframe."""
    return {
        word.strip(): row["ARTI"]
        for _, row in df.iterrows()
        for word in (row["LEMA"].lower() + "," + row["SUBLEMA"].lower()).split(",")
        if word.strip()
    }

def build_phrase_dict(df: pd.DataFrame, phrase_col: str, meaning_col: str) -> Dict[str, str]:
    """Build phrase dictionary (idiom/paribasa)."""
    return {
        phrase.lower(): meaning
        for phrase, meaning in zip(df[phrase_col], df[meaning_col])
        if pd.notna(meaning)
    }

def translate_text(
    text: str,
    kamus_dict: Dict[str, str],
    idiom_dict: Dict[str, str],
    paribasa_dict: Dict[str, str]
) -> str:
    """Translate text using the provided dictionaries."""
    words = re.findall(r"\b\w+\b|[.,!?;]", text)
    translated = []
    i = 0
    
    while i < len(words):
        # Check 2-word phrases first
        if i < len(words) - 1:
            phrase = " ".join(words[i:i+2]).lower()
            if phrase in idiom_dict:
                translated.append(idiom_dict[phrase])
                i += 2
                continue
            if phrase in paribasa_dict:
                translated.append(paribasa_dict[phrase])
                i += 2
                continue
        
        # Single word translation
        word = words[i].lower()
        translated.append(kamus_dict.get(word, word))
        i += 1
    
    return " ".join(translated)
