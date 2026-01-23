import pdfplumber
import google.generativeai as genai
import json
import os
import requests
from pathlib import Path

# 1. CONFIGURACIÓN
API_KEY = "" # Cambia esto por tu llave real
genai.configure(api_key=API_KEY)

# Configuración de carpetas
INPUT_JSON = "../data/uartes_careers.json"  # Cambia por el nombre de tu archivo
OUTPUT_DIR = Path("../data_malla")
TEMP_PDF_DIR = Path("temp_pdfs")

# Asegurar que existan los directorios
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_PDF_DIR.mkdir(parents=True, exist_ok=True)

def descargar_pdf(url, nombre_archivo):
    ruta_local = TEMP_PDF_DIR / nombre_archivo
    try:
        response = requests.get(url, stream=True, timeout=20)
        response.raise_for_status()
        with open(ruta_local, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return str(ruta_local)
    except Exception as e:
        print(f"Error descargando {url}: {e}")
        return None

def extraer_texto_pdf(ruta_pdf):
    texto_total = ""
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto_total += f"\n--- PÁGINA {i+1} ---\n"
                texto_total += pagina.extract_text(layout=True) or ""
        return texto_total
    except Exception as e:
        return f"Error al leer el PDF: {e}"

def procesar_malla_con_ia(ruta_pdf):
    texto_extraido = extraer_texto_pdf(ruta_pdf)
    
    # Usando el modelo estable más rápido
    model = genai.GenerativeModel(
        model_name='gemini-3-flash-preview',
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = f"""
    Analiza visualmente este texto de una malla curricular y extrae los datos en formato JSON.
    
    Extrae:
    - universidad (nombre de la institución)
    - carrera (nombre del programa)
    - pensum (año o versión)
    - materias (lista de objetos: codigo, nombre, creditos, horas, semestre)
    - totales (objeto: total_creditos, total_horas)

    Es vital que revises cada semestre. Si un dato no es legible o entendible, pon "null".
    
    TEXTO:
    {texto_extraido}
    """

    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Fallo en IA: {str(e)}"}

def main():
    # Cargar datos del spider de Scrapy
    if not os.path.exists(INPUT_JSON):
        print(f"No se encontró el archivo {INPUT_JSON}")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        carreras_scrapy = json.load(f)

    lista_final_formateada = []

    for item_scrapy in carreras_scrapy:
        nombre_carrera = item_scrapy.get("career_name", "sin_nombre").replace(" ", "_")
        url_pdf = item_scrapy.get("study_plan_pdf")

        if not url_pdf or url_pdf == "null":
            continue

        print(f"--- Procesando: {item_scrapy.get('career_name')} ---")
        
        # 1. Descargar
        ruta_pdf = descargar_pdf(url_pdf, f"{nombre_carrera}.pdf")

        if ruta_pdf:
            # 2. Procesar con IA
            datos_ia = procesar_malla_con_ia(ruta_pdf)
            
            # 3. CONSTRUIR EL FORMATO ESPECÍFICO
            # Aquí "aplanamos" el JSON para que quede como tu ejemplo
            objeto_formateado = {
                "universidad": datos_ia.get("universidad", "Universidad de las Artes"),
                "carrera": item_scrapy.get("career_name"), # Usamos el nombre limpio del spider
                "career_url_ref": item_scrapy.get("career_url", "https://www.uartes.edu.ec/sitio/la-universidad/pregrado/"), 
                "pensum": datos_ia.get("pensum", "Vigente"),
                "materias": datos_ia.get("materias", []),
                "totales": datos_ia.get("totales", {"total_creditos": 0, "total_horas": 0})
            }
            
            lista_final_formateada.append(objeto_formateado)
            
            # Opcional: eliminar PDF para no llenar el disco
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)

    # 4. Guardar un solo JSON con todas las carreras
    archivo_final = OUTPUT_DIR / "mallas_unificadas.json"
    with open(archivo_final, "w", encoding="utf-8") as f:
        json.dump(lista_final_formateada, f, indent=4, ensure_ascii=False)
    
    print(f"\n¡Éxito! Archivo creado en: {archivo_final}")

if __name__ == "__main__":
    main()