import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

import google.generativeai as genai

import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from google.api_core.exceptions import ResourceExhausted


# =========================
# CONFIGURACIÓN TESSERACT
# =========================
pytesseract.pytesseract.tesseract_cmd = r"C:\Archivos de programa\Tesseract-OCR\tesseract.exe"


# =========================
# VARIABLES DE ENTORNO
# =========================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ No se encontró GEMINI_API_KEY")

genai.configure(api_key=API_KEY)


# =========================
# RUTAS DEL PROYECTO
# =========================
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DATA_UNIDREAM = ROOT_DIR / "Data_UniDream"

INPUT_JSON = DATA_UNIDREAM / "data" / "ecotec_careers.json"
OUTPUT_DIR = DATA_UNIDREAM / "data_malla"

TEMP_PDF_DIR = BASE_DIR / "temp_pdfs"
TEMP_IMG_DIR = BASE_DIR / "temp_images"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_PDF_DIR.mkdir(parents=True, exist_ok=True)
TEMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# UTILIDADES
# =========================
def descargar_pdf(url, nombre):
    ruta = TEMP_PDF_DIR / nombre
    try:
        r = requests.get(url, timeout=30, verify=False)
        r.raise_for_status()
        with open(ruta, "wb") as f:
            f.write(r.content)
        return ruta
    except Exception as e:
        print(f"❌ Error descargando PDF: {e}")
        return None


def pdf_tiene_texto(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    for page in doc:
        texto = page.get_text().strip()
        if len(texto) > 50:  # evita falsos positivos
            return True
    return False


def extraer_texto_pdf_directo(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    texto = ""
    for i, page in enumerate(doc, 1):
        texto += f"\n--- PÁGINA {i} ---\n"
        texto += page.get_text("text")
    return texto


def pdf_a_imagenes(ruta_pdf):
    imagenes = convert_from_path(ruta_pdf, dpi=350)
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
            config="--psm 6"
        )
        texto_total += f"\n--- PÁGINA {i+1} ---\n{texto}"
    return texto_total


def extraer_texto_inteligente(ruta_pdf):
    if pdf_tiene_texto(ruta_pdf):
        print("📄 Texto vectorial detectado → sin OCR")
        return extraer_texto_pdf_directo(ruta_pdf)
    else:
        print("🖼️ PDF escaneado → usando OCR")
        rutas_img = pdf_a_imagenes(ruta_pdf)
        return ocr_imagenes(rutas_img)


def filtrar_texto_malla(texto):
    palabras_clave = [
        "SEMESTRE", "ASIGNATURA", "MATERIA",
        "CRÉDITO", "CREDITO", "HORAS"
    ]
    lineas = []
    for l in texto.splitlines():
        if any(p in l.upper() for p in palabras_clave):
            lineas.append(l)
    return "\n".join(lineas)


def parsear_json_seguro(texto):
    try:
        texto = texto.strip()
        if texto.startswith("```"):
            texto = texto.split("```")[1]
        return json.loads(texto)
    except Exception as e:
        print("⚠️ Error parseando JSON:", e)
        return {}


# =========================
# IA – EXTRACCIÓN
# =========================
def procesar_malla_con_ia(texto, intentos=3):
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = f"""
Eres un extractor de datos estructurados.

Devuelve SOLO un JSON con esta estructura exacta:

{{
  "universidad": string|null,
  "carrera": string|null,
  "pensum": string|null,
  "materias": [
    {{
      "codigo": string|null,
      "nombre": string,
      "creditos": number|null,
      "horas": number|null,
      "semestre": number|null
    }}
  ],
  "totales": {{
    "total_creditos": number|null,
    "total_horas": number|null
  }}
}}

Reglas:
- No inventes datos
- Si una materia no es clara, no la incluyas
- Usa null si el dato no aparece

TEXTO:
{texto}
"""

    for intento in range(1, intentos + 1):
        try:
            response = model.generate_content(prompt)
            return parsear_json_seguro(response.text)

        except ResourceExhausted as e:
            espera = 30 * intento
            print(f"⏳ Cuota excedida. Reintentando en {espera}s (intento {intento}/{intentos})")
            time.sleep(espera)

        except Exception as e:
            print("❌ Error inesperado en Gemini:", e)
            break

    return {}

def limpiar_temporales():
    for carpeta in [TEMP_PDF_DIR, TEMP_IMG_DIR]:
        for archivo in carpeta.iterdir():
            archivo.unlink()


# =========================
# MAIN
# =========================
def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        carreras = json.load(f)

    resultado_final = []

    for item in carreras:
        carrera = item.get("career_name")
        url_pdf = item.get("study_plan_pdf")

        if not url_pdf:
            continue

        print(f"\n📄 Procesando: {carrera}")

        nombre_pdf = carrera.replace(" ", "_").replace("/", "-") + ".pdf"
        ruta_pdf = descargar_pdf(url_pdf, nombre_pdf)

        if not ruta_pdf:
            continue

        texto = extraer_texto_inteligente(ruta_pdf)
        texto = filtrar_texto_malla(texto)

        datos_ia = procesar_malla_con_ia(texto)

        time.sleep(15)  # límite API gratuita

        resultado_final.append({
            "universidad": datos_ia.get("universidad") or item.get("university_name"),
            "carrera": carrera,
            "career_url_ref": item.get("career_url"),
            "pensum": datos_ia.get("pensum"),
            "materias": datos_ia.get("materias", []),
            "totales": datos_ia.get("totales", {})
        })

        limpiar_temporales()

    salida = OUTPUT_DIR / "ecotec_mallas.json"
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=4, ensure_ascii=False)

    print("\n✅ PROCESO FINALIZADO")
    print("📁 Archivo generado en:", salida)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
