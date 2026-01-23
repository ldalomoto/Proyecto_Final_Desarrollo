import json
import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Configuración de rutas
INPUT_FOLDER = "../data_ia_ready"
OUTPUT_FILE = "../embeddings/career_embeddings.pkl"

def load_all_careers(folder):
    """Carga todas las carreras de todos los archivos JSON en la carpeta."""
    all_careers = []
    files = [f for f in os.listdir(folder) if f.endswith('_with_text.json')]
    
    for file_name in files:
        with open(os.path.join(folder, file_name), 'r', encoding='utf-8') as f:
            all_careers.extend(json.load(f))
    return all_careers

def create_embeddings():
    # 2. Cargar el modelo de IA localmente
    print("⏳ Cargando modelo SentenceTransformer (esto puede tardar la primera vez)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 3. Cargar datos
    careers = load_all_careers(INPUT_FOLDER)
    if not careers:
        print("❌ No se encontraron archivos con el campo 'unified_text'.")
        return

    # 4. Extraer los textos y metadatos
    texts = [c["unified_text"] for c in careers]
    metadata = [{
        "career_id": c["career_id"],
        "career_name": c["career_name"],
        "university_name": c["university_name"],
        "career_url": c.get("career_url", "")
    } for c in careers]

    # 5. Generar vectores
    print(f"🚀 Generando embeddings para {len(texts)} carreras...")
    embeddings = model.encode(texts, show_progress_bar=True)

    # 6. Guardar todo en un archivo pickle
    data_to_save = {
        "embeddings": embeddings,
        "metadata": metadata,
        "model_name": 'all-MiniLM-L6-v2'
    }

    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(data_to_save, f)

    print(f"✅ ¡Éxito! Archivo guardado: {OUTPUT_FILE}")
    print(f"📊 Dimensiones de la matriz: {embeddings.shape}")

if __name__ == "__main__":
    create_embeddings()