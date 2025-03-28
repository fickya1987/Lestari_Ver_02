import re
import pandas as pd
import random
from typing import Tuple, List, Dict, Set

def clean_text(text: str) -> str:
    """Clean text by removing punctuation and normalizing."""
    return re.sub(r"[^\w\s-]", "", text.lower())

def is_loma(df: pd.DataFrame, word: str) -> bool:
    """Check if word is categorized as LOMA."""
    row = df[df["LEMA"].str.lower() == word.lower()]
    if not row.empty:
        category = row["(HALUS/LOMA/KASAR)"].values[0]
        return pd.notna(category) and "LOMA" in category.upper()
    return False

def process_constraints(text: str, df_kamus: pd.DataFrame) -> Tuple[List[str], List[str], List[str], Dict[str, str], Set[str], Set[str]]:
    """Core constraint processing logic."""
    # [Keep all the existing constraint processing code...]
    # [Same implementation you already have in your constraint_text function]
    # [Just rename the function to process_constraints]

def highlight_text(translated_text: str, df_kamus: pd.DataFrame) -> str:
    """Highlight text based on dictionary constraints."""
    (kata_terdapat, kata_tidak_terdapat, 
     kata_terdapat_tidak_loma, pasangan_kata, 
     kata_e_petik, kata_e_petik2) = process_constraints(translated_text, df_kamus)
    
    hasil_lines = []
    for baris in translated_text.splitlines():
        kata_list = baris.split()
        hasil_baris = []
        
        for word in kata_list:
            # [Keep your existing highlighting logic here]
            # [Same implementation you already have]
            
        hasil_lines.append(" ".join(hasil_baris))
    
    return "<br>".join(hasil_lines)

# Explicitly expose the public functions
__all__ = ['highlight_text', 'process_constraints']
