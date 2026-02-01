import json
import os
import re
import unicodedata
from datetime import date
from difflib import SequenceMatcher

# =========================
# NORMALIZACIÓN
# =========================

def normalize(text):
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"\s+", " ", text)
    return text

# =========================
# RUTAS
# =========================

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "Data_UniDream", "data")
MALLA_DIR = os.path.join(BASE_DIR, "Data_UniDream", "data_malla")

CAREERS_FILE = os.path.join(DATA_DIR, "ecotec_careers.json")
MALLA_FILE = os.path.join(MALLA_DIR, "ecotec_mallas.json")
OUTPUT_FILE = os.path.join(MALLA_DIR, "ecotec_unificada.json")

# =========================
# CARGA
# =========================

with open(CAREERS_FILE, "r", encoding="utf-8") as f:
    careers = json.load(f)

with open(MALLA_FILE, "r", encoding="utf-8") as f:
    mallas = json.load(f)

# =========================
# LOOKUP DE MALLAS
# =========================

malla_lookup = {}
for m in mallas:
    key = (
        normalize(m.get("universidad")),
        normalize(m.get("carrera"))
    )
    malla_lookup[key] = m.get("materias", [])

# =========================
# UNIFICACIÓN
# =========================

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

result = []

for c in careers:
    uni_norm = normalize(c.get("university_name"))
    career_norm = normalize(c.get("career_name"))

    best_match = None
    best_score = 0

    for (u_norm, c_norm), materias in malla_lookup.items():
        if u_norm != uni_norm:
            continue

        score = similarity(career_norm, c_norm)

        if score > best_score:
            best_score = score
            best_match = materias

    # Umbral de aceptación
    if best_score >= 0.80:
        materias_final = best_match
    else:
        materias_final = []

    unified = {
        **c,
        "study_plan_name": f"Malla Curricular {c.get('career_name')}",
        "subjects": [
            {
                "code": m.get("codigo"),
                "name": m.get("nombre"),
                "semester": m.get("semestre"),
                "credits": m.get("creditos"),
                "hours": m.get("horas")
            }
            for m in materias_final
        ],
        "match_score": round(best_score, 2),
        "data_unified_date": date.today().strftime("%Y-%m-%d")
    }

    result.append(unified)

# =========================
# GUARDADO
# =========================

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"✅ Unificación ECOTEC completada → {OUTPUT_FILE}")
