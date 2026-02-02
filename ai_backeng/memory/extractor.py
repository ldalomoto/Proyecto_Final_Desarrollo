import google.generativeai as genai
import json
import os
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carga las variables del archivo .env al entorno de Python
load_dotenv()

# Extrae la API Key y configúrala
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ No se encontró la GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=GEMINI_API_KEY)

# Ahora puedes instanciar el modelo usando tus preferencias
model = genai.GenerativeModel(
    model_name="gemini-2.5-pro", # El modelo que elegimos para mucho texto
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json"
    }
)

# =========================
# Utils
# =========================
def set_nested(data: dict, path: str, value):
    keys = path.split(".")
    for k in keys[:-1]:
        if k not in data or not isinstance(data[k], dict):
            data[k] = {}
        data = data[k]
    data[keys[-1]] = value

# =========================
# Extractor principal (Versión Gemini)
# =========================
def extract_profile_updates(user_message: str, current_profile: dict):
    # En Gemini no necesitas "limpieza defensiva" de triple backticks si usas JSON mode
    prompt = f"""
    Eres un experto en extracción de entidades. Tu objetivo es actualizar el perfil vocacional del usuario.
    
    MENSAJE DEL USUARIO:
    "{user_message}"
    
    PERFIL ACTUAL (Como referencia):
    {json.dumps(current_profile)}

    INSTRUCCIÓN:
    Extrae información nueva. Si el usuario contradice algo anterior, prevalece la información NUEVA.
    Responde estrictamente con un objeto JSON que contenga los campos:
    nombre, ciudad, modalidad, universidad_publica, habilidades, intereses, materias_fuertes, materias_debiles, has_career_intent.
    """

    try:
        # Generar contenido
        response = model.generate_content(prompt)
        
        # Con response_mime_type: "application/json", response.text ya es un JSON puro
        updates = json.loads(response.text)

        print("====== GEMINI JSON RESPONSE ======")
        print(json.dumps(updates, indent=2))
        print("==================================")

        # =========================
        # MERGE + NORMALIZACIÓN (Tu lógica original se mantiene igual)
        # =========================
        updated_profile = json.loads(json.dumps(current_profile))

        if "nombre" in updates: updated_profile["nombre"] = updates["nombre"]
        if "ciudad" in updates: set_nested(updated_profile, "preferencias.ciudad", updates["ciudad"])
        if "modalidad" in updates: set_nested(updated_profile, "preferencias.modalidad", updates["modalidad"])
        if "universidad_publica" in updates: 
            set_nested(updated_profile, "preferencias.universidad_publica", updates["universidad_publica"])

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
        print(f"❌ Error en extractor Gemini: {e}")
        return {"profile_data": current_profile, "has_career_intent": False}