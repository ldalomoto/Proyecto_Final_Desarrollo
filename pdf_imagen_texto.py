import pdfplumber
import google.generativeai as genai
import json
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from pdf2image import convert_from_path
from PIL import Image
import warnings

warnings.filterwarnings("ignore")

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

INPUT_JSON = os.path.abspath(
    os.path.join(BASE_DIR, "..", "Data_Inidream", "data_borradores", f"{universidad}_careers.json")
)

OUTPUT_DIR = Path(os.path.join(BASE_DIR, "..", "Data_Inidream", "data_malla"))
TEMP_PDF_DIR = Path(os.path.join(BASE_DIR, "temp_pdfs"))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_PDF_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# 3. FUNCIONES
# =========================
def descargar_pdf(url, nombre_archivo):
    ruta_local = TEMP_PDF_DIR / nombre_archivo
    try:
        response = requests.get(url, stream=True, timeout=30, verify=False)
        response.raise_for_status()
        with open(ruta_local, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return str(ruta_local)
    except Exception as e:
        print(f"Error descargando {url}: {e}")
        return None


def pdf_a_imagenes(ruta_pdf, dpi=300):
    rutas_imagenes = []
    try:
        paginas = convert_from_path(ruta_pdf, dpi=dpi)
        for i, pagina in enumerate(paginas):
            nombre_img = f"{Path(ruta_pdf).stem}_pag_{i+1}.png"
            ruta_img = TEMP_PDF_DIR / nombre_img
            pagina.save(ruta_img, "PNG")
            rutas_imagenes.append(str(ruta_img))
        return rutas_imagenes
    except Exception as e:
        print(f"Error convirtiendo PDF a imágenes: {e}")
        return []


def procesar_malla_con_ia_imagenes(rutas_imagenes):
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = """
    Analiza visualmente esta malla curricular universitaria y extrae los datos en formato JSON.

    Extrae estrictamente:
    - universidad
    - carrera
    - pensum
    - materias (lista de objetos: codigo, nombre, creditos, horas, semestre)
    - totales (total_creditos, total_horas)

    Reglas:
    - Revisa cada semestre cuidadosamente
    - Si un dato no es legible o no existe, usa null
    - No inventes información
    - Devuelve SOLO JSON válido
    """

    partes = [prompt]

    for ruta in rutas_imagenes:
        with open(ruta, "rb") as f:
            partes.append({
                "mime_type": "image/png",
                "data": f.read()
            })

    try:
        response = model.generate_content(partes)
        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Fallo en IA: {str(e)}"}

# =========================
# 4. MAIN
# =========================
def main():
    print("🔍 Buscando JSON en:", INPUT_JSON)

    if not os.path.exists(INPUT_JSON):
        print(f"No se encontró el archivo {INPUT_JSON}")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        carreras_scrapy = json.load(f)

    lista_final_formateada = []
    contador_api = 0

    for item_scrapy in carreras_scrapy:
        nombre_limpio = item_scrapy.get("career_name", "sin_nombre") \
            .replace(" ", "_").replace("/", "-")

        nombre_archivo = f"{nombre_limpio}.pdf"
        url_pdf = item_scrapy.get("study_plan_pdf")

        if not url_pdf or url_pdf == "null":
            continue

        if contador_api > 0 and contador_api % 5 == 0:
            print("\n" + "!"*40)
            print(f"Procesados {contador_api} elementos.")
            nueva_key = input("🔑 Ingresa una NUEVA API KEY: ").strip()
            genai.configure(api_key=nueva_key)
            print("API actualizada.\n" + "!"*40)

        print(f"--- Procesando ({contador_api + 1}): {item_scrapy.get('career_name')} ---")

        ruta_pdf = descargar_pdf(url_pdf, nombre_archivo)
        if not ruta_pdf:
            continue

        # PDF → IMÁGENES
        imagenes = pdf_a_imagenes(ruta_pdf)
        if not imagenes:
            os.remove(ruta_pdf)
            continue

        # IA CON IMÁGENES
        datos_ia = procesar_malla_con_ia_imagenes(imagenes)

        if isinstance(datos_ia, list) and datos_ia:
            datos_ia = datos_ia[0]

        if not isinstance(datos_ia, dict):
            datos_ia = {}

        objeto_formateado = {
            "universidad": datos_ia.get("universidad") or "Escuela Politécnica Nacional",
            "carrera": item_scrapy.get("career_name"),
            "career_url_ref": item_scrapy.get("career_url") or url_pdf,
            "pensum": datos_ia.get("pensum") or "Vigente",
            "materias": datos_ia.get("materias") if isinstance(datos_ia.get("materias"), list) else [],
            "totales": datos_ia.get("totales") if isinstance(datos_ia.get("totales"), dict)
                       else {"total_creditos": 0, "total_horas": 0}
        }

        lista_final_formateada.append(objeto_formateado)

        # LIMPIEZA
        for img in imagenes:
            if os.path.exists(img):
                os.remove(img)

        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)

        contador_api += 1

    archivo_final = OUTPUT_DIR / f"{universidad}_mallas2.json"
    with open(archivo_final, "w", encoding="utf-8") as f:
        json.dump(lista_final_formateada, f, indent=4, ensure_ascii=False)

    print(f"\n✅ ¡Éxito! Archivo creado en: {archivo_final}")

# =========================
# 5. ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
