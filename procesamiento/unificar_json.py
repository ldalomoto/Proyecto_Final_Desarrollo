import json
import re
import os

def generate_id(name):
    # Genera un ID simple: Comunicación Corporativa -> COM_CORP
    words = re.findall(r'\b\w{3,}', name.upper())
    return "_".join(words[:2])

def merge_and_save(careers_data, subjects_data):
    # 1. Crear la carpeta de destino si no existe
    output_folder = "data_unificada"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Carpeta '{output_folder}' creada.")

    # 2. Diccionario para búsqueda rápida de materias
    subjects_lookup = {
        (s['universidad'], s['carrera']): s['materias'] 
        for s in subjects_data
    }

    # 3. Agruparemos por universidad para crear archivos separados
    universities_files = {}

    for career in careers_data:
        uni_name = career['university_name']
        key = (uni_name, career['career_name'])
        raw_subjects = subjects_lookup.get(key, [])
        
        formatted_subjects = [
            {
                "code": sub['codigo'],
                "name": sub['nombre'].split("  ")[0].strip().title(),
                "semester": sub['semestre']
            }
            for sub in raw_subjects
        ]
        
        unified_career = {
            "career_id": generate_id(career['career_name']),
            "career_name": career['career_name'],
            "university": uni_name,
            "description": career.get('description', ""),
            "duration": career.get('duration', ""),
            "modality": career.get('modality', ""),
            "study_plan_url": career.get('study_plan_url', ""),
            "subjects": formatted_subjects
        }

        # Inicializar lista para la universidad si es la primera vez que aparece
        if uni_name not in universities_files:
            universities_files[uni_name] = []
        
        universities_files[uni_name].append(unified_career)

    # 4. Guardar cada universidad en su propio archivo
    for uni_name, data in universities_files.items():
        # Limpiar el nombre de la universidad para que sea un nombre de archivo válido
        filename = re.sub(r'[^\w\s-]', '', uni_name).replace(' ', '_').lower() + ".json"
        filepath = os.path.join(output_folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Archivo guardado: {filepath}")

# --- Ejecución ---
try:
    with open('../data/uartes_careers.json', 'r', encoding='utf-8') as f:
        careers = json.load(f)
    with open('../data_malla/uartes_mallas.json', 'r', encoding='utf-8') as f:
        subjects = json.load(f)

    merge_and_save(careers, subjects)
except FileNotFoundError as e:
    print(f"Error: No se encontró el archivo {e.filename}")