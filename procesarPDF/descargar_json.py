import pdfplumber
import google.generativeai as genai
import json
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# =========================
# 1. CARGA DE VARIABLES DE ENTORNO
# =========================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("No se encontró la GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=API_KEY)

# =========================
# 2. CONFIGURACIÓN DE RUTAS SEGURAS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

universidad = "epn"  # Cambiar según la universidad que se esté procesando

# JSON de entrada generado por Scrapy
INPUT_JSON = os.path.abspath(
    os.path.join(BASE_DIR, "..", "data", f"{universidad}_careers.json")
)

# Carpetas de salida y PDFs temporales
OUTPUT_DIR = Path(os.path.join(BASE_DIR, "..", "data_malla"))
TEMP_PDF_DIR = Path(os.path.join(BASE_DIR, "temp_pdfs"))

# Crear carpetas si no existen
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_PDF_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# 3. FUNCIONES
# =========================
def descargar_pdf(url, nombre_archivo):
    ruta_local = TEMP_PDF_DIR / nombre_archivo
    try:
        # Agregamos verify=False para saltar la validación del certificado SSL
        response = requests.get(url, stream=True, timeout=20, verify=False)
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

# =========================
# 4. MAIN
# =========================
def main():
    # Debug: mostrar la ruta real del JSON
    print("🔍 Buscando JSON en:", INPUT_JSON)

    # Verificar que el JSON exista
    if not os.path.exists(INPUT_JSON):
        print(f"No se encontró el archivo {INPUT_JSON}")
        return

    # Cargar datos del spider Scrapy
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        carreras_scrapy = json.load(f)

    lista_final_formateada = []
    
    # --- CONTADOR PARA EL CAMBIO DE API ---
    contador_api = 0

    for item_scrapy in carreras_scrapy:
        nombre_limpio = item_scrapy.get("career_name", "sin_nombre").replace(" ", "_").replace("/", "-")
        
        # Opcional: limpiar también otros caracteres problemáticos
        nombre_archivo = f"{nombre_limpio}.pdf"
        
        url_pdf = item_scrapy.get("study_plan_pdf")

        if not url_pdf or url_pdf == "null":
            continue

        #"https://www.utc.edu.ec/Portals/0/2025/Extensión Pujilí/MALLA2  GRÁFICA PEDAGOGÍA DE LA MATEMÁTICA Y LA FÍSICA -  15-02-2022 ANEXO 5 - CORREGIDA 2025.pdf?ver=2025-10-16-163043-593",

        #url_valida = ["https://www.epn.edu.ec/wp-content/uploads/2025/01/malla_seguridad_redes_informacion.pdf",
        #              "https://www.epn.edu.ec/wp-content/uploads/2025/01/malla_software.pdf",
        #              "https://www.epn.edu.ec/wp-content/uploads/2025/01/malla_matematica_aplicada.pdf",
        #              "https://www.epn.edu.ec/wp-content/uploads/2024/08/malla_tecnologias_informacion.pdf",
        #              "https://www.epn.edu.ec/wp-content/uploads/2025/01/malla_procesamiento_madera.pdf",
        #              "https://www.epn.edu.ec/wp-content/uploads/2025/01/malla_tecnologias_informacion.pdf"]
        #
        #if url_pdf not in url_valida:
        #    continue

        # Lógica de cambio de API cada 10 procesamientos exitosos o intentos
        if contador_api > 0 and contador_api % 5 == 0:
            print("\n" + "!"*40)
            print(f"Se han procesado {contador_api} elementos.")
            nueva_key = input("🔑 Límite de lote. Ingresa una NUEVA API KEY para continuar: ").strip()
            genai.configure(api_key=nueva_key)
            print("Configuración actualizada. Continuando...")
            print("!"*40 + "\n")

        print(f"--- Procesando ({contador_api + 1}): {item_scrapy.get('career_name')} ---")
        
        # Usar el nombre_archivo ya limpio
        ruta_pdf = descargar_pdf(url_pdf, nombre_archivo)

        if ruta_pdf:
            # 2. Procesar con IA
            datos_ia = procesar_malla_con_ia(ruta_pdf)
            
            # --- VALIDACIÓN PARA EVITAR ERROR 'list object has no attribute get' ---
            if isinstance(datos_ia, list) and len(datos_ia) > 0:
                datos_ia = datos_ia[0]
            
            if not isinstance(datos_ia, dict):
                datos_ia = {}
            # ----------------------------------------------------------------------
            
            # 3. Construir el JSON final
            objeto_formateado = {
                "universidad": datos_ia.get("university_name") or "Universidad Tecnica de Cotopaxi",
                "carrera": item_scrapy.get("career_name"),
                "career_url_ref": item_scrapy.get("career_url") or url_pdf, 
                "pensum": datos_ia.get("pensum") or "Vigente",
                "materias": datos_ia.get("materias") if isinstance(datos_ia.get("materias"), list) else [],
                "totales": datos_ia.get("totales") if isinstance(datos_ia.get("totales"), dict) else {"total_creditos": 0, "total_horas": 0}
            }
            
            lista_final_formateada.append(objeto_formateado)
            
            # 4. Opcional: eliminar PDF temporal
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)
            
            # Aumentar contador solo si hubo un intento de procesamiento
            contador_api += 1

    # Guardar todas las carreras en un solo JSON
    archivo_final = OUTPUT_DIR / f"{universidad}_mallas2.json"
    with open(archivo_final, "w", encoding="utf-8") as f:
        json.dump(lista_final_formateada, f, indent=4, ensure_ascii=False)
    
    print(f"\n¡Éxito! Archivo creado en: {archivo_final}")

# =========================
# 5. ENTRY POINT
# =========================
if __name__ == "__main__":
    main()

