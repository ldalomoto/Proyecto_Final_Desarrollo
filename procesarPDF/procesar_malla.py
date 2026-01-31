import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Nueva librería recomendada
from google import genai 
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# =========================
# 0. CONFIGURACIÓN DE RUTAS EXTERNAS
# =========================
# Indica a Python dónde están instalados los programas
pytesseract.pytesseract.tesseract_cmd = r'C:\Archivos de programa\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Archivos de programa\Tesseract-OCR\tessdata'
# Cambia esta ruta a donde hayas extraído Poppler
PATH_POPPLER = r'C:\poppler-24.08.0\Library\bin' 

# =========================
# 1. VARIABLES DE ENTORNO
# =========================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ No se encontró GEMINI_API_KEY en el archivo .env")

# Nuevo cliente de Google GenAI
client = genai.Client(api_key=API_KEY)

# =========================
# 2. RUTAS DEL PROYECTO
# =========================
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DATA_UNIDREAM = ROOT_DIR / "Data_UniDream"

INPUT_JSON = DATA_UNIDREAM / "data" / "uide_careers.json"
OUTPUT_DIR = DATA_UNIDREAM / "data_malla"
TEMP_PDF_DIR = BASE_DIR / "temp_pdfs"
TEMP_IMG_DIR = BASE_DIR / "temp_images"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_PDF_DIR.mkdir(parents=True, exist_ok=True)
TEMP_IMG_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# 3. FUNCIONES
# =========================
def descargar_pdf(url, nombre):
    ruta = TEMP_PDF_DIR / nombre
    try:
        # verify=True es mejor, pero si el sitio de la U falla, mantenlo en False
        r = requests.get(url, stream=True, timeout=30, verify=False)
        r.raise_for_status()
        with open(ruta, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return ruta
    except Exception as e:
        print(f"❌ Error descargando PDF: {e}")
        return None

def pdf_a_imagenes(ruta_pdf):
    # Aquí usamos la ruta de Poppler
    imagenes = convert_from_path(ruta_pdf, dpi=300, poppler_path=PATH_POPPLER)
    rutas = []
    for i, img in enumerate(imagenes):
        ruta_img = TEMP_IMG_DIR / f"{ruta_pdf.stem}_p{i+1}.png"
        img.save(ruta_img, "PNG")
        rutas.append(ruta_img)
    return rutas

def ocr_imagenes(rutas):
    texto_total = ""
    for i, ruta in enumerate(rutas):
        try:
            texto = pytesseract.image_to_string(Image.open(ruta), lang="spa", config="--psm 6")
            texto_total += f"\n--- PÁGINA {i+1} ---\n{texto}"
        except Exception as e:
            print(f"❌ Error en OCR página {i+1}: {e}")
    return texto_total

def extraer_texto_pdf(ruta_pdf):
    rutas_img = pdf_a_imagenes(ruta_pdf)
    return ocr_imagenes(rutas_img)

def procesar_malla_con_ia(texto):
    prompt = f"Analiza esta MALLA CURRICULAR y genera un JSON con: universidad, carrera, pensum, materias (codigo, nombre, creditos, semestre) y totales.\n\nTEXTO:\n{texto}"
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Usando el modelo más actual
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

def limpiar_temporales():
    for carpeta in [TEMP_PDF_DIR, TEMP_IMG_DIR]:
        for archivo in carpeta.iterdir():
            archivo.unlink()

# =========================
# 4. MAIN
# =========================
def main():
    if not INPUT_JSON.exists():
        print(f"❌ No existe {INPUT_JSON}")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        carreras = json.load(f)

    resultado_final = []

    for i, item in enumerate(carreras, 1):
        carrera = item.get("career_name")
        url_pdf = item.get("study_plan_pdf")

        if not url_pdf or url_pdf == "null":
            continue

        print(f"📄 ({i}/{len(carreras)}) Procesando: {carrera}")
        nombre_pdf = f"{carrera.replace(' ', '_')}.pdf"
        ruta_pdf = descargar_pdf(url_pdf, nombre_pdf)

        if ruta_pdf:
            texto = extraer_texto_pdf(ruta_pdf)
            datos_ia = procesar_malla_con_ia(texto)
            
            resultado_final.append({
                "universidad": datos_ia.get("universidad") or item.get("university_name"),
                "carrera": carrera,
                "materias": datos_ia.get("materias", []),
                "totales": datos_ia.get("totales", {})
            })
            limpiar_temporales()

    with open(OUTPUT_DIR / "uide_mallas.json", "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=4, ensure_ascii=False)
    print("\n✅ PROCESO FINALIZADO")

if __name__ == "__main__":
    main()