import requests
import json
import re
import os


# =========================
# Ollama config (Docker-safe)
# =========================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"


# =========================
# Utils
# =========================
def set_nested(data: dict, path: str, value):
    """
    Setea valores en dicts anidados usando path tipo:
    preferencias.ciudad
    """
    keys = path.split(".")
    for k in keys[:-1]:
        if k not in data or not isinstance(data[k], dict):
            data[k] = {}
        data = data[k]
    data[keys[-1]] = value


# =========================
# Extractor principal
# =========================
def extract_profile_updates(user_message: str, current_profile: dict):
    prompt = f"""
Actúa como un extractor de entidades para un sistema de orientación vocacional.

MENSAJE DEL USUARIO:
\"\"\"{user_message}\"\"\"

Extrae SOLO información nueva explícita en JSON.

CAMPOS POSIBLES:
- nombre (str)
- ciudad (str)
- modalidad (str)
- universidad_publica (bool true/false)
- habilidades (list)
- intereses (list)
- materias_fuertes (list)
- materias_debiles (list)
- has_career_intent (bool)

REGLAS:
1. Si no hay info, NO incluyas el campo.
2. Responde SOLO con JSON válido.
3. No agregues texto fuera del JSON.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 500
                }
            },
            timeout=300
        )
        response.raise_for_status()

        raw_text = response.json().get("response", "").strip()

        print("====== OLLAMA RAW RESPONSE ======")
        print(raw_text)
        print("=================================")

        # Limpieza defensiva
        raw_text = re.sub(r"```json|```", "", raw_text).strip()
        raw_text = re.sub(r"\bTrue\b", "true", raw_text)
        raw_text = re.sub(r"\bFalse\b", "false", raw_text)

        updates = json.loads(raw_text)

        # =========================
        # MERGE + NORMALIZACIÓN
        # =========================
        updated_profile = json.loads(json.dumps(current_profile))  # deep copy segura

        # 🔹 Campos simples
        if "nombre" in updates:
            updated_profile["nombre"] = updates["nombre"]

        # 🔹 Preferencias
        if "ciudad" in updates:
            set_nested(updated_profile, "preferencias.ciudad", updates["ciudad"])

        if "modalidad" in updates:
            set_nested(updated_profile, "preferencias.modalidad", updates["modalidad"])

        if "universidad_publica" in updates:
            set_nested(
                updated_profile,
                "preferencias.universidad_publica",
                updates["universidad_publica"]
            )

        # 🔹 Listas (merge sin duplicados)
        LIST_MAP = {
            "intereses": "intereses",
            "habilidades": "habilidades_percibidas",
            "materias_fuertes": "materias_fuertes",
            "materias_debiles": "materias_debiles"
        }

        for src, dst in LIST_MAP.items():
            if src in updates and isinstance(updates[src], list):
                updated_profile.setdefault(dst, [])
                current_set = set(updated_profile[dst])

                for item in updates[src]:
                    item = str(item).lower().strip()
                    if item and item not in current_set:
                        updated_profile[dst].append(item)

        return {
            "profile_data": updated_profile,
            "has_career_intent": bool(updates.get("has_career_intent", False))
        }

    except Exception as e:
        print(f"❌ Error en extractor Ollama: {e}")
        return {
            "profile_data": current_profile,
            "has_career_intent": False
        }

