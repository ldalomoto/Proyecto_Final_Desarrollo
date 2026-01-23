import pickle
import numpy as np
import os
import warnings
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Desactivar advertencias de symlinks de HuggingFace en Windows/Debian
warnings.filterwarnings("ignore", category=UserWarning)

# 1. Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_PKL = os.path.join(BASE_DIR, "..", "embeddings", "career_embeddings.pkl")

def search_loop():
    # Verificar si el archivo existe
    if not os.path.exists(PATH_PKL):
        print(f"❌ Error: No se encontró el archivo en: {PATH_PKL}")
        return

    # 2. Cargar el "cerebro" una sola vez al inicio
    print("⏳ Cargando base de conocimientos...")
    with open(PATH_PKL, 'rb') as f:
        data = pickle.load(f)
    
    embeddings = data["embeddings"]
    metadata = data["metadata"]
    model = SentenceTransformer(data.get("model_name", 'all-MiniLM-L6-v2'))
    
    print("✅ Sistema listo. Escribe 'salir' para terminar.")

    while True:
        print("\n" + "="*60)
        query_text = input("👉 Introduce una carrera o interés: ").strip()

        if query_text.lower() in ['salir', 'exit', 'quit']:
            print("👋 Saliendo del buscador...")
            break
        
        if not query_text:
            continue

        # 3. Procesar búsqueda
        # Truco: Duplicamos el peso de la consulta para mejorar la puntería
        query_vector = model.encode([query_text])
        
        # 4. Calcular similitud coseno
        similarities = cosine_similarity(query_vector, embeddings)[0]
        
        # 5. Obtener TOP 5
        top_indices = np.argsort(similarities)[::-1][:5]
        
        print(f"\n🔍 Resultados para: '{query_text}'")
        print("-" * 60)
        
        for i, idx in enumerate(top_indices):
            score = similarities[idx]
            item = metadata[idx]
            
            # Formato visual mejorado para la DEMO
            print(f"{i+1}. {item['career_name'].upper()}")
            print(f"   🏛️  {item['university_name']}")
            print(f"   🎯 Similitud: {score:.4%}") # Mostramos como porcentaje
            print("-" * 60)

if __name__ == "__main__":
    try:
        search_loop()
    except KeyboardInterrupt:
        print("\n\nTerminado por el usuario.")