import json
import os
import re

def clean_subject_name(name):
    """Limpia nombres de materias quitando el texto en inglés."""
    if not name: return ""
    return name.split("  ")[0].strip().title()

def generate_career_text(career):
    """Genera el bloque de texto narrativo para la IA."""
    # Extraer datos básicos
    name = career.get("career_name", "Sin nombre")
    uni = career.get("university_name", "Sin universidad")
    desc = career.get("description", "Sin descripción disponible.")
    mod = career.get("modality", "Presencial")
    dur = career.get("duration", "N/A")
    
    # Procesar materias (máximo 15 para no saturar el contexto si es necesario)
    subjects = career.get("subjects", [])
    subject_names = [clean_subject_name(s.get("name")) for s in subjects]
    
    # Si hay demasiadas materias, podemos unirlas por comas
    materias_str = ", ".join(subject_names[:30]) # Tomamos las primeras 30
    
    # Construcción del texto unificado
    text = (
        f"Carrera: {name}. "
        f"Universidad: {uni}. "
        f"Modalidad: {mod}. "
        f"Duración: {dur}. "
        f"Descripción: {desc} "
        f"Materias principales: {materias_str}."
    )
    return text

def process_all_universities(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Listar todos los archivos JSON en la carpeta de unificada
    files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

    for file_name in files:
        input_path = os.path.join(input_folder, file_name)
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        new_data = []
        for career in data:
            # Generamos el texto y lo inyectamos en el objeto
            career["unified_text"] = generate_career_text(career)
            new_data.append(career)

        # Guardar el nuevo archivo
        output_name = file_name.replace(".json", "_with_text.json")
        output_path = os.path.join(output_folder, output_name)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Procesado: {file_name} -> {output_name}")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Ajusta estas carpetas según tu estructura local
    CARPETA_ENTRADA = "../data_unificada"
    CARPETA_SALIDA = "../data_ia_ready"
    
    process_all_universities(CARPETA_ENTRADA, CARPETA_SALIDA)