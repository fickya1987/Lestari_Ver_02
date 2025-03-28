import re
import pandas as pd
from typing import Tuple, List, Dict, Set

def clean_text(text: str) -> str:
    """Clean text by removing punctuation and normalizing."""
    return re.sub(r"[^\w\s-]", "", text.lower())

def constraint_text(text: str, df_kamus: pd.DataFrame) -> Tuple[List[str], List[str], List[str], Dict[str, str], Set[str], Set[str]]:
    """Process text against dictionary constraints."""
    # Clean and prepare text
    text_clean = clean_text(text.replace("-", " "))
    words = set(text_clean.split())
    
    # Prepare dictionary data
    df_e_petik = df_kamus[df_kamus["LEMA"].str.contains("[éÉ]", na=False, regex=True)]
    df_e_petik.loc[:, "LEMA"] = df_e_petik["LEMA"].str.replace("[éÉ]", "e", regex=True)
    kata_e_petik = {kata.lower() for kata in df_e_petik["LEMA"].astype(str)}
    
    # Similar processing for other special characters...
    
    # Get words from dictionary
    kata_dataframe1 = {kata.lower() for kata in df_kamus["LEMA"].astype(str)}
    kata_dataframe2 = {
        kata.strip().replace(".", "")
        for kata_list in df_kamus["SUBLEMA"].astype(str)
        for kata in kata_list.split(",")
        if kata.strip()
    }
    
    # Combine all dictionary words
    dictionary_words = kata_dataframe1 | kata_dataframe2 | kata_e_petik
    
    # Categorize words
    found_words = sorted(words.intersection(dictionary_words))
    found_words = [w for w in found_words if not re.search(r"\d", w)]
    
    not_found_words = sorted(words - dictionary_words)
    not_found_words = [w for w in not_found_words if not re.search(r"\d", w)]
    
    # Process synonyms and replacements
    replacements = {}
    non_loma_words = []
    
    for word in found_words[:]:
        row = df_kamus[df_kamus["LEMA"].str.lower() == word]
        if not row.empty:
            category = row["(HALUS/LOMA/KASAR)"].values[0]
            if pd.notna(category) and "LOMA" not in category.upper():
                synonyms = row["SINONIM"].values[0] if pd.notna(row["SINONIM"].values[0]) else ""
                loma_synonyms = [
                    s.strip() for s in synonyms.split(",") 
                    if s.strip() and is_loma(df_kamus, s.strip())
                ]
                
                if loma_synonyms:
                    replacements[word] = random.choice(loma_synonyms)
                else:
                    not_found_words.append(word)
                    found_words.remove(word)
                    non_loma_words.append(word)
    
    return found_words, not_found_words, non_loma_words, replacements, kata_e_petik, set()

def is_loma(df: pd.DataFrame, word: str) -> bool:
    """Check if word is categorized as LOMA."""
    row = df[df["LEMA"].str.lower() == word.lower()]
    if not row.empty:
        category = row["(HALUS/LOMA/KASAR)"].values[0]
        return pd.notna(category) and "LOMA" in category.upper()
    return False
