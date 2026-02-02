import json
import re
import os
import unicodedata
from datetime import date

# --- 1. Funciones de ayuda y normalización ---

def clean_text_simple(text):
    """Limpia espacios extra y saltos de línea."""
    if not text: return ""
    return " ".join(text.split()).strip()

def normalize_key(text):
    """
    Normaliza una cadena para usarla como clave de búsqueda:
    - Convierte a mayúsculas.
    - Elimina tildes.
    - Elimina caracteres no alfanuméricos.
    - Elimina palabras conectores (de, del, en, y) para mejorar coincidencias.
    """
    if not text: return ""
    
    # 1. Convertir a mayúsculas
    text = text.upper()
    
    # 2. Eliminar tildes (NFD split)
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
    # 3. Reemplazar caracteres especiales por espacios y limpiar
    text = re.sub(r'[^A-Z0-9]', ' ', text)
    
    # 4. Eliminar palabras irrelevantes para el cruce (stopwords)
    stopwords = ["DE", "DEL", "LA", "EL", "EN", "Y", "LOS", "LAS", "II", "I"]
    words = text.split()
    filtered_words = [w for w in words if w not in stopwords]
    
    return "".join(filtered_words) # Retorna ej: "MARKETING", "GESTIONTALENTOHUMANO"

def generate_global_id(uni_name, modality, career_name):
    """Genera un ID único formateado."""
    siglas_map = {
        "UNIVERSIDAD TECNOLOGICA ECOTEC": "ECOTEC",
        "UNIVERSIDAD DE LAS AMERICAS": "UDLA",
        "ESCUELA POLITECNICA NACIONAL": "EPN"
    }
    
    # Normalizar nombre universidad para buscar sigla
    uni_norm = normalize_key(uni_name)
    # Buscar sigla, si no existe, toma las primeras 6 letras
    sigla = "ECOTEC" if "ECOTEC" in uni_norm else uni_norm[:6]
    
    mod = re.sub(r'\W+', '_', modality.upper()) if modality else "PRESENCIAL"
    name = re.sub(r'\W+', '_', career_name.upper()) if career_name else "CARRERA"
    
    # Eliminar tildes del ID final
    id_str = f"{sigla}_{mod}_{name}"
    return ''.join(c for c in unicodedata.normalize('NFD', id_str) if unicodedata.category(c) != 'Mn')

# --- 2. Función Principal de Unión ---

def merge_and_save(careers_data, subjects_data):
    output_folder = "Data_UniDream/data_unificada"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # --- CREAR DICCIONARIO DE BÚSQUEDA (LOOKUP) ---
    subjects_lookup = {}
    print("--- Indexando Mallas ---")
    for s in subjects_data:
        uni_raw = s.get('universidad', '').strip()
        carrera_raw = s.get('carrera', '').strip()
        
        # Generamos la clave normalizada
        key_uni = normalize_key(uni_raw)
        key_career = normalize_key(carrera_raw)
        
        full_key = (key_uni, key_career)
        
        # Guardamos en el diccionario
        subjects_lookup[full_key] = s['materias']
        # Debug: ver qué claves se están generando
        # print(f"Clave generada mallas: {full_key}")

    universities_files = {}
    matches_found = 0

    print("\n--- Cruzando Carreras ---")
    for career in careers_data:
        uni_name = career.get('university_name', 'Desconocida').strip()
        career_name = career.get('career_name', 'Sin Nombre').strip()
        modality = career.get('modality', 'Presencial')

        # Generar clave de búsqueda normalizada para esta carrera
        search_key = (normalize_key(uni_name), normalize_key(career_name))
        
        # Buscar materias
        raw_subjects = subjects_lookup.get(search_key, [])
        
        if raw_subjects:
            matches_found += 1
            # print(f"✅ Coincidencia encontrada para: {career_name}")
        else:
            # Opcional: Imprimir fallos para depurar
            # print(f"⚠️ No se halló malla para: {career_name} (Clave: {search_key})")
            pass

        formatted_subjects = []
        for sub in raw_subjects:
            full_name = sub.get('nombre') or sub.get('name', "")
            # Limpieza básica del nombre de la materia
            clean_name = full_name.strip()
            
            formatted_subjects.append({
                "code": sub.get('codigo') or sub.get('code'),
                "name": clean_name,
                "semester": sub.get('semestre') or sub.get('semester')
            })

        # Si no hubo coincidencia pero el JSON original tenía 'subjects', usarlos
        if not formatted_subjects and 'subjects' in career:
            formatted_subjects = career['subjects']

        # Construcción del objeto final
        unified_career = {
            "career_id": generate_global_id(uni_name, modality, career_name),
            "university_name": uni_name,
            "career_url": career.get('career_url') or career.get('study_plan_url', ""),
            "data_collection_date": date.today().strftime("%Y-%m-%d"),
            "university_type": career.get('university_type', "Privada"),
            "university_contact": career.get('university_contact', ""),
            "career_name": career_name,
            "faculty_name": career.get('faculty') or career.get('faculty_name', "General"),
            "degree_title": career.get('degree_title', ""),
            "description": career.get('description', ""),
            "locations": career.get('locations', ["Ecuador"]),
            "cost": career.get('cost', "Consultar"),
            "semesters": career.get('semesters', "4 años"), # Usar 'semesters' si 'duration' no existe
            "modality": modality,
            "study_plan_name": f"Malla Curricular {career_name}",
            "study_plan_pdf": career.get('study_plan_pdf', "No disponible"),
            "subjects": formatted_subjects
        }

        if uni_name not in universities_files:
            universities_files[uni_name] = []
        
        universities_files[uni_name].append(unified_career)

    # --- Guardado ---
    for uni_name, data in universities_files.items():
        # Limpiar nombre de archivo
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', normalize_key(uni_name)).lower()
        filename = f"{safe_name}.json"
        filepath = os.path.join(output_folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📂 Archivo guardado: {filepath}")
        print(f"📊 Total carreras procesadas: {len(data)}")
        print(f"🔗 Total cruces exitosos (con materias): {matches_found}")

# --- Ejecución (Asegúrate de que las rutas sean correctas) ---
# NOTA: En este entorno no puedo leer tus carpetas locales, 
# pero este bloque asume que los archivos existen en las rutas indicadas.

try:
    # Rutas definidas en tu código original
    path_c = os.path.join('Data_UniDream/data', 'ecotec_careers.json')
    path_m = os.path.join('Data_UniDream/data_malla', 'ecotec_mallas.json')
    
    print(f"Leyendo: {path_c}")
    with open(path_c, 'r', encoding='utf-8') as f:
        c_data = json.load(f)
    
    m_data = []
    if os.path.exists(path_m):
        print(f"Leyendo: {path_m}")
        with open(path_m, 'r', encoding='utf-8') as f:
            m_data = json.load(f)
    else:
        print("⚠️ No se encontró el archivo de mallas.")

    merge_and_save(c_data, m_data)

except FileNotFoundError:
    print("❌ Error: No se encontraron los archivos JSON en las rutas especificadas.")
    print("Asegúrate de que la carpeta 'Data_UniDream' esté en el mismo directorio que este script.")
except Exception as e:
    print(f"❌ Error inesperado: {e}")