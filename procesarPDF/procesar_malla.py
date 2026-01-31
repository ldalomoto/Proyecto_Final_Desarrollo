import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import re

import google.generativeai as genai
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# =========================
# 0. CONFIGURACIÓN DE RUTAS EXTERNAS
# =========================
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
PATH_POPPLER = r'C:\poppler-25.12.0\Library\bin'

# =========================
# 1. VARIABLES DE ENTORNO
# =========================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ No se encontró GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=API_KEY)

# =========================
# 2. RUTAS DEL PROYECTO
# =========================
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DATA_UNIDREAM = ROOT_DIR / "Data_UniDream"

universidad = "uide"

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

def limpiar_texto(texto):
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.replace('|', ' ')
    return texto.strip()

def filtrar_lineas_materias(texto):
    lineas = texto.split("\n")
    posibles = []

    for l in lineas:
        l = l.strip()

        if len(l) > 15 and any(char.isdigit() for char in l):
            if any(p in l.lower() for p in ["sem", "cred", "hor", "mat", "adm", "ing", "cal"]):
                posibles.append(l)

    return "\n".join(posibles)

def descargar_pdf(url, nombre):
    ruta = TEMP_PDF_DIR / nombre
    try:
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
    imagenes = convert_from_path(ruta_pdf, dpi=500, poppler_path=PATH_POPPLER)
    rutas = []

    for i, img in enumerate(imagenes):
        ruta_img = TEMP_IMG_DIR / f"{ruta_pdf.stem}_p{i+1}.png"
        img.save(ruta_img, "PNG")
        rutas.append(ruta_img)

    return rutas

def ocr_imagenes(rutas):
    texto_total = ""
    for i, ruta in enumerate(rutas):
        texto = pytesseract.image_to_string(
            Image.open(ruta),
            lang="spa",
            config="--psm 4 -c preserve_interword_spaces=1"
        )
        texto_total += f"\n{texto}\n"
    return texto_total

def extraer_texto_pdf(ruta_pdf):
    rutas_img = pdf_a_imagenes(ruta_pdf)
    return ocr_imagenes(rutas_img)

def procesar_malla_con_ia(texto):
    texto = limpiar_texto(texto)
    texto = filtrar_lineas_materias(texto)

    if len(texto) < 50:
        return {"materias": []}

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.1
        }
    )

    prompt = f"""
Extrae materias universitarias desde estas filas OCR.

Responde SOLO JSON válido.

Formato EXACTO:

{{
 "materias":[
   {{
     "codigo": "string|null",
     "nombre": "string|null",
     "creditos": number|null",
     "horas": number|null",
     "semestre": number|null"
   }}
 ]
}}

FILAS:
{texto}
"""

    try:
        response = model.generate_content(prompt)
        datos = json.loads(response.text)

        if "materias" not in datos or not isinstance(datos["materias"], list):
            datos["materias"] = []

        return datos

    except Exception as e:
        return {"error": str(e), "materias": []}

def limpiar_temporales():
    for carpeta in [TEMP_PDF_DIR, TEMP_IMG_DIR]:
        for archivo in carpeta.iterdir():
            archivo.unlink()

# =========================
# 4. MAIN
# =========================
def main():
    print("📂 Leyendo carreras desde:", INPUT_JSON)

    if not INPUT_JSON.exists():
        print("❌ No existe uide_careers.json")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        carreras = json.load(f)

    resultado_final = []

    for i, item in enumerate(carreras, 1):
        carrera = item.get("career_name")
        url_pdf = item.get("study_plan_pdf")

        if not url_pdf or url_pdf == "null":
            continue

        print(f"\n📄 Procesando: {carrera}")

        nombre_pdf = carrera.replace(" ", "_").replace("/", "-") + ".pdf"
        ruta_pdf = descargar_pdf(url_pdf, nombre_pdf)

        if not ruta_pdf:
            continue

        texto = extraer_texto_pdf(ruta_pdf)
        datos_ia = procesar_malla_con_ia(texto)

        resultado_final.append({
            "universidad": item.get("university_name"),
            "carrera": carrera,
            "career_url_ref": item.get("career_url"),
            "pensum": None,
            "materias": datos_ia.get("materias", []),
            "totales": {}
        })

        limpiar_temporales()

    archivo_salida = OUTPUT_DIR / "uide_mallas.json"
    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=4, ensure_ascii=False)

    print("\n✅ PROCESO FINALIZADO")
    print("📁 Archivo creado en:", archivo_salida)

# =========================
# 5. ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
