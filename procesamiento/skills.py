import json
import hashlib
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# =========================
# 1. CONFIGURACIÓN GENERAL
# =========================

MODEL_NAME = "google/flan-t5-large"

INPUT_DIR = Path("../data_unificada")
OUTPUT_DIR = Path("../data_skills_final")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COUNTRY = "Ecuador"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"🧠 Cargando modelo en {DEVICE}...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    device_map="auto" if DEVICE == "cuda" else None
).to(DEVICE)

# =========================
# 2. UTILIDADES
# =========================

def gen_id(prefix, text):
    base = f"{prefix}_{text}".encode("utf-8")
    return f"{prefix}_{hashlib.sha1(base).hexdigest()[:10]}"

def safe(value, default=""):
    return value if value is not None else default

def limpiar_skill(texto):
    return texto.strip().lower()

# =========================
# 3. PROMPT PRINCIPAL (POR CARRERA)
# =========================

def generar_prompt_carrera(career, subjects):
    materias = "\n".join([f"- {s}" for s in subjects])

    return f"""
Dada la siguiente carrera universitaria en Ecuador, genera habilidades
profesionales DESCRIPTIVAS para cada materia.

Carrera: {career['career_name']}
Universidad: {career['university_name']}
Facultad: {career.get('faculty_name', '')}
Descripción de la carrera:
{career.get('description', '')[:600]}

Materias:
{materias}

INSTRUCCIONES:
- Idioma: español
- Para CADA materia genera entre 8 y 12 habilidades
- Las habilidades deben ser profesionales y aplicables
- No usar palabras genéricas como "conocimiento de"
- Responder SOLO en JSON válido

FORMATO EXACTO:
{{
  "Materia 1": ["habilidad 1", "habilidad 2"],
  "Materia 2": ["habilidad 1", "habilidad 2"]
}}
"""

# =========================
# 4. LLAMADA AL MODELO LOCAL
# =========================

def inferir_skills(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(DEVICE)

    outputs = model.generate(
        **inputs,
        max_new_tokens=1200,
        temperature=0.3,
        do_sample=False
    )

    texto = tokenizer.decode(outputs[0], skip_special_tokens=True)

    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        print("⚠️ El modelo devolvió JSON inválido, se omite esta carrera")
        return {}

# =========================
# 5. PIPELINE PRINCIPAL
# =========================

def main():
    resultado_final = []

    for archivo in INPUT_DIR.glob("*.json"):
        print(f"\n📂 Procesando archivo: {archivo.name}")

        with open(archivo, "r", encoding="utf-8") as f:
            try:
                careers = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ JSON inválido, se omite archivo")
                continue

        for career in careers:
            career_name = safe(career.get("career_name"), "Carrera desconocida")
            career_id = safe(career.get("career_id"), gen_id("career", career_name))
            university = safe(career.get("university_name"))
            locations = career.get("locations", [])

            print(f"🎓 Carrera: {career_name}")

            subjects = career.get("subjects", [])
            subject_names = [safe(s.get("name")) for s in subjects if safe(s.get("name"))]

            if not subject_names:
                continue

            prompt = generar_prompt_carrera(career, subject_names)
            skills_por_materia = inferir_skills(prompt)

            subjects_out = []
            all_skills_flat = set()

            for subject in subjects:
                name = safe(subject.get("name"))
                if name not in skills_por_materia:
                    continue

                subject_id = gen_id("subject", career_id + name)

                skills_objs = []
                for sk in skills_por_materia[name]:
                    sk_clean = limpiar_skill(sk)
                    skill_id = gen_id("skill", sk_clean)
                    skills_objs.append({
                        "skill_id": skill_id,
                        "name": sk_clean
                    })
                    all_skills_flat.add(sk_clean)

                subjects_out.append({
                    "subject_id": subject_id,
                    "code": safe(subject.get("code")),
                    "name": name,
                    "semester": safe(subject.get("semester")),
                    "skills": skills_objs
                })

                print(f"  ✅ Skills generadas: {name}")

            resultado_final.append({
                "career_id": career_id,
                "career_name": career_name,
                "university_name": university,
                "country": COUNTRY,
                "locations": locations,
                "subjects": subjects_out,
                "career_general_skills": [
                    {
                        "skill_id": gen_id("skill", sk),
                        "name": sk
                    }
                    for sk in sorted(all_skills_flat)
                ]
            })

    output_file = OUTPUT_DIR / "careers_skills_ecuador.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=2, ensure_ascii=False)

    print(f"\n🚀 Proceso terminado → {output_file}")

# =========================
# 6. EJECUCIÓN
# =========================

if __name__ == "__main__":
    main()
