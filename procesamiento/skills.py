import json
import os
import re
from sentence_transformers import SentenceTransformer, util
import torch

# Modelo multilingüe
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Conceptos que DEFINEN una habilidad
SKILL_PROMPT_VECTORS = model.encode([
    "habilidad técnica",
    "destreza profesional",
    "competencia laboral",
    "capacidad práctica",
    "professional skill",
    "technical skill",
    "expertise",
    "competency",
    "capability",
    "proficiency",
    "know-how"
], convert_to_tensor=True)

def is_skill_related(text, threshold=0.8):
    """
    Determina si un texto tiene alta carga semántica de habilidad
    """
    if not text or len(text.strip()) < 4:
        return False, 0.0

    emb = model.encode(text, convert_to_tensor=True)
    score = util.cos_sim(emb, SKILL_PROMPT_VECTORS).max().item()

    return score >= threshold, score

def process_with_high_confidence():
    input_file = '../data_unificada/UDLA.json'
    output_dir = 'data_inteligente'
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for career in data:
        career_skills = []

        for subject in career.get('subjects', []):
            name = subject.get('name', '')

            is_skill, confidence = is_skill_related(name)

            subject['skill_confidence'] = round(confidence, 3)
            subject['is_skill_related'] = is_skill

            if is_skill:
                career_skills.append(name)
                print(f"✅ {name} ({confidence:.2f})")

        career['career_skill_related_subjects'] = career_skills

    output_path = os.path.join(output_dir, 'UDLA_high_confidence.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    process_with_high_confidence()
