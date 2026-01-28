import google.generativeai as genai
import json

def extract_profile_updates(user_message: str, current_profile: dict):
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # Le pasamos el perfil actual para que sepa qué NO debe borrar
    prompt = f"""
    Eres un transcriptor de datos. Tu único trabajo es actualizar un perfil de usuario en formato JSON.
    
    PERFIL ACTUAL:
    {json.dumps(current_profile)}
    
    MENSAJE NUEVO DEL USUARIO:
    "{user_message}"
    
    REGLAS ESTRICTAS:
    1. Si el usuario da información nueva (nombre, ciudad, gustos), agrégala.
    2. SI EL USUARIO NO MENCIONA ALGO QUE YA ESTABA EN EL PERFIL, MANTÉN EL DATO ANTERIOR. No lo borres ni lo pongas en null.
    3. Para 'intereses' y 'habilidades', añade los nuevos a la lista existente sin duplicados.
    4. Responde EXCLUSIVAMENTE con el JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        # Limpiamos posibles etiquetas de markdown ```json ... ```
        raw_text = response.text.strip().replace("```json", "").replace("```", "")
        updated_data = json.loads(raw_text)
        
        # Validamos que no nos devuelva basura
        if isinstance(updated_data, dict) and "intereses" in updated_data:
            return updated_data
    except Exception as e:
        print(f"Error en extractor: {e}")
    
    return current_profile # Si algo falla, devolvemos lo que ya teníamos intacto