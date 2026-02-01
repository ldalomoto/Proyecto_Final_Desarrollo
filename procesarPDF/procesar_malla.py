import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

import google.generativeai as genai
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# Agrega esta línea con la ruta que aparece en tu imagen:
pytesseract.pytesseract.tesseract_cmd = r'C:\Archivos de programa\Tesseract-OCR\tesseract.exe'

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
BASE_DIR = Path(__file__).resolve().parent          # procesarPDF/
ROOT_DIR = BASE_DIR.parent                          # PROYECTO_FINAL_DESARROLLO/
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


def extraer_texto_pdf(ruta_pdf):
    rutas_img = pdf_a_imagenes(ruta_pdf)
    return ocr_imagenes(rutas_img)


def procesar_malla_con_ia(texto):
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = f"""
Analiza el siguiente texto de una MALLA CURRICULAR universitaria y genera un JSON.

Extrae estrictamente:
- universidad
- carrera
- pensum
- materias (lista con: codigo, nombre, creditos, horas, semestre)
- totales (total_creditos, total_horas)

Si un dato no es claro, usa null.

TEXTO:
{texto}
"""

    try:
        response = model.generate_content(prompt)
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
    print("📂 Leyendo carreras desde:", INPUT_JSON)

    if not INPUT_JSON.exists():
        print("❌ No existe uide_careers.json")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        carreras = json.load(f)

    resultado_final = []

    for i, item in enumerate(carreras, 1):
        carrera = item.get("career_name")
        url_pdf = item.get("study_plan_pdf")  # 🔑 AQUÍ SE TOMAN LOS LINKS

        if not url_pdf or url_pdf == "null":
            print(f"⚠️ Sin PDF para: {carrera}")
            continue

        print(f"\n📄 ({i}) Procesando:", carrera)

        nombre_pdf = carrera.replace(" ", "_").replace("/", "-") + ".pdf"
        ruta_pdf = descargar_pdf(url_pdf, nombre_pdf)

        if not ruta_pdf:
            continue

        texto = extraer_texto_pdf(ruta_pdf)
        datos_ia = procesar_malla_con_ia(texto)

        if isinstance(datos_ia, list):
            datos_ia = datos_ia[0]

        if not isinstance(datos_ia, dict):
            datos_ia = {}

        resultado_final.append({
            "universidad": datos_ia.get("universidad") or item.get("university_name"),
            "carrera": carrera,
            "career_url_ref": item.get("career_url"),
            "pensum": datos_ia.get("pensum"),
            "materias": datos_ia.get("materias", []),
            "totales": datos_ia.get("totales", {})
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