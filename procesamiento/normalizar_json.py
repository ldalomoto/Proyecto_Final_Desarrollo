import json
import re
import os
import nltk
from nltk.corpus import words

# Descargar diccionarios de palabras la primera vez
nltk.download('words')
ENGLISH_WORDS = set(w.lower() for w in words.words())

def clean_bilingual_with_nlp(text):
    if not text:
        return ""

    # Palabras que existen en español y no queremos que confundan (falsos amigos)
    # Puedes ampliar esta lista si detectas errores
    SPANISH_EXCEPTIONS = {"plan", "digital", "social", "marketing", "gestion", "radio", "video", "musical", "instrumental"}
    ROMANS = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"}

    tokens = text.split()
    clean_tokens = []
    
    for i, word in enumerate(tokens):
        word_clean = re.sub(r'[^\w]', '', word).lower()
        
        # Si la palabra es un número romano, la mantenemos pero chequeamos si se repite
        if word.upper() in ROMANS:
            # Si el romano ya estaba en la lista, significa que empezó la traducción
            if word.upper() in [t.upper() for t in clean_tokens]:
                break
            clean_tokens.append(word.upper())
            continue

        # Si la palabra es larga y está en el diccionario inglés pero NO es una excepción española
        if len(word_clean) > 3 and word_clean in ENGLISH_WORDS and word_clean not in SPANISH_EXCEPTIONS:
            # Verificamos si la palabra anterior también suena a inglés o si ya tenemos suficiente texto
            if i > 0: 
                break 
        
        clean_tokens.append(word)

    # Re-armar el texto
    result = " ".join(clean_tokens).strip().title()
    
    # Corregir conectores a minúsculas
    conectores = ["De", "En", "Y", "La", "Los", "A", "Para", "Del", "E"]
    final_words = [result.split()[0]] if result.split() else []
    for w in result.split()[1:]:
        if w.upper() in ROMANS:
            final_words.append(w.upper())
        else:
            final_words.append(w.lower() if w in conectores else w)
            
    return " ".join(final_words)

def get_initials(name):
    mapping = {"Universidad de Las Américas": "UDLA"}
    if name in mapping: return mapping[name]
    return "".join([w[0] for w in name.upper().split() if w not in ["DE", "LAS", "LA", "LOS", "DEL"]])

def process_and_save():
    output_dir = "data_normalizada"
    os.makedirs(output_dir, exist_ok=True)

    with open('data/udla_careers.json', 'r', encoding='utf-8') as f:
        careers = json.load(f)
    with open('data_malla/udla_mallas.json', 'r', encoding='utf-8') as f:
        subjects = json.load(f)
            
    subjects_map = {(s['universidad'], s['carrera']): s['materias'] for s in subjects}
    uni_groups = {}

    for c in careers:
        uni = c['university_name']
        clean_name = clean_bilingual_with_nlp(c['career_name'])
        raw_mats = subjects_map.get((uni, c['career_name']), [])
        
        clean_mats = [
            {
                "code": m['codigo'],
                "name": clean_bilingual_with_nlp(m['nombre']),
                "semester": m['semestre']
            } for m in raw_mats
        ]

        obj = {
            "career_id": "_".join(re.findall(r'\b\w{3,}', clean_name.upper())[:2]),
            "career_name": clean_name,
            "university": uni,
            "description": c.get('description', ""),
            "duration": c.get('duration', ""),
            "modality": c.get('modality', ""),
            "subjects": clean_mats
        }

        if uni not in uni_groups: uni_groups[uni] = []
        uni_groups[uni].append(obj)

    for uni, data in uni_groups.items():
        filename = f"{get_initials(uni)}_normal.json"
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Normalizado con NLTK: {filename}")

if __name__ == "__main__":
    process_and_save()