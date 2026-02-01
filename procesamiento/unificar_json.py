import json
import re
import os
from datetime import date

def clean_text_simple(text):
    """Limpia espacios extra y saltos de línea."""
    if not text: return ""
    return " ".join(text.split()).strip()

def generate_global_id(uni_name, modality, career_name):
    """Genera un ID único: UDLA_PRESENCIAL_CIENCIAS_POLITICAS"""
    siglas_map = {
        "Universidad de Cuenca": "UCUENCA",
        "Universidad Internacional del Ecuador": "UIDE",
        "Universidad de las Artes": "UARTES",
        "Universidad de Las Américas": "UDLA",
        "Escuela Politécnica Nacional": "EPN",
        "Universidad Técnica de Cotopaxi": "UTC",
        "Universidad Técnológica ECOTEC": "ECOTEC"
    }
    sigla = siglas_map.get(uni_name, re.sub(r'\W+', '', uni_name[:6]).upper())
    
    # Limpiar modalidad y nombre para el ID
    mod = re.sub(r'\W+', '_', modality.upper()) if modality else "PRESENCIAL"
    name = re.sub(r'\W+', '_', career_name.upper()) if career_name else "CARRERA"
    
    return f"{sigla}_{mod}_{name}"

def merge_and_save(careers_data, subjects_data):
    output_folder = "Data_UniDream/data_unificada"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 1. Diccionario de búsqueda (Lookup) corregido
    # Usamos .strip() para evitar que espacios invisibles rompan el cruce
    subjects_lookup = {
        (s['universidad'].strip(), s['carrera'].strip()): s['materias'] 
        for s in subjects_data
    }

    universities_files = {}

    for career in careers_data:
        uni_name = career.get('university_name', 'Desconocida').strip()
        career_name = career.get('career_name', 'Sin Nombre').strip()
        modality = career.get('modality', 'Presencial')
        
        # 2. Buscar materias en el lookup
        key = (uni_name, career_name)
        raw_subjects = subjects_lookup.get(key, [])
        
        formatted_subjects = []
        for sub in raw_subjects:
            # Limpiamos el nombre de la materia (quitamos el nombre en inglés si existe)
            full_name = sub.get('nombre') or sub.get('name', "")
            clean_name = full_name.split("  ")[0].strip().title() # Toma solo la parte en español
            
            formatted_subjects.append({
                "code": sub.get('codigo') or sub.get('code'),
                "name": clean_name,
                "semester": sub.get('semestre') or sub.get('semester')
            })
        
        # Si el Scrapy ya traía materias (caso UCuenca), las usamos como respaldo
        if not formatted_subjects and 'subjects' in career:
            formatted_subjects = career['subjects']

        # 3. Mapeo de variables ajustado a tu JSON de UDLA
        unified_career = {
            "career_id": generate_global_id(uni_name, modality, career_name),
            "university_name": uni_name,
            "career_url": career.get('career_url') or career.get('study_plan_url', ""),
            "data_collection_date": date.today().strftime("%Y-%m-%d"),
            "university_type": career.get('university_type', "Privada"),
            "university_contact": career.get('university_contact', ""),
            "career_name": career_name,
            "faculty_name": career.get('faculty') or career.get('faculty_name', "General"), # Ajuste aquí
            "degree_title": career.get('degree_title', ""),
            "description": career.get('description', ""),
            "locations": career.get('locations', ["Ecuador"]),
            "cost": career.get('cost', "Consultar"),
            "duration": career.get('duration', ""),
            "modality": modality,
            "study_plan_name": f"Malla Curricular {career_name}",
            "study_plan_pdf": career.get('study_plan_url') or career.get('study_plan_pdf', "No disponible"),
            "subjects": formatted_subjects
        }

        if uni_name not in universities_files:
            universities_files[uni_name] = []
        
        universities_files[uni_name].append(unified_career)

    # 4. Guardar archivos
    for uni_name, data in universities_files.items():
        filename = re.sub(r'\W+', '_', uni_name).lower() + ".json"
        filepath = os.path.join(output_folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Integración completada: {filepath} ({len(data)} carreras)")

# --- Ejecución ---
files_to_process = [
    ('ecotec_careers.json', 'ecotec_mallas.json')
]

for career_file, malla_file in files_to_process:
    try:
        # Ajusta las rutas según tu estructura de carpetas
        path_c = os.path.join('Data_UniDream/data', career_file)
        path_m = os.path.join('Data_UniDream/data_malla', malla_file)
        
        if not os.path.exists(path_c):
            print(f"❌ No existe: {path_c}")
            continue

        with open(path_c, 'r', encoding='utf-8') as f:
            c_data = json.load(f)
        
        m_data = []
        if os.path.exists(path_m):
            with open(path_m, 'r', encoding='utf-8') as f:
                m_data = json.load(f)
        else:
            print(f"⚠️ No se encontró archivo de mallas para {career_file}, se unificará sin materias.")

        merge_and_save(c_data, m_data)
    except Exception as e:
        print(f"Omitiendo {career_file} debido a un error: {e}")