import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

import google.generativeai as genai
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# ======================================================
# CONFIGURACIÓN DE TESSERACT (NO TOCAR)
# ======================================================
pytesseract.pytesseract.tesseract_cmd = r'C:\Archivos de programa\Tesseract-OCR\tesseract.exe'

# ======================================================
# 1. VARIABLES DE ENTORNO (GEMINI)
# ======================================================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ No se encontró GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=API_KEY)

# ======================================================
# 2. RUTAS DEL PROYECTO
# ======================================================
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

DATA_UNIDREAM = ROOT_DIR / "Data_UniDream"
OUTPUT_DIR = DATA_UNIDREAM / "data_malla"

TEMP_PDF_DIR = BASE_DIR / "temp_pdfs"
TEMP_IMG_DIR = BASE_DIR / "temp_images"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_PDF_DIR.mkdir(parents=True, exist_ok=True)
TEMP_IMG_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================
# 3. LISTA MANUAL DE MALLAS PENDIENTES (🔥 CAMBIO CLAVE 🔥)
# ======================================================
# 👉 Aquí colocas SOLO las carreras que NO se lograron scrapear
# 👉 Puedes ir agregando / quitando sin tocar nada más del código

MALLAS_PENDIENTES = [
    {
    "career_name": "Finanzas y Negocios Digitales",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2026/01/malla-finanzas-y-negocios-dig.-uio-2026.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-finanzas-y-negocios-digitales/"
    },
    {
    "career_name": "Enfermería Nocturna",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2025/12/malla-enfermeria-2025.pdf",
    "career_url": "https://www.uide.edu.ec/enfermeria-nocturna/"
    },
    {
    "career_name": "Enfermería",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2025/12/malla-enfermeria-2025.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-enfermeria/"
    },
    {
    "career_name": "Diseño Gráfico",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2024/02/Malla-Diseno-Grafico-2024.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-diseno-grafico/"
    },
    {
    "career_name": "Derecho (En Línea)",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2026/01/derecho.pdf",
    "career_url": "https://www.uide.edu.ec/derecho-en-linea/"
    },
    {
    "career_name": "Derecho",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2024/08/malla-derecho-uio-2024.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-derecho/"
    },
    {
    "career_name": "Contabilidad y Auditoría (En Línea)",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2025/09/contabilidad-y-auditoria-2025-2.pdf",
    "career_url": "https://www.uide.edu.ec/contabilidad-y-auditoria-en-linea/"
    },
    {
    "career_name": "Comunicación y Medios Digitales (En Línea)",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2025/09/malla-comunicacion-y-medios-digitales-actualizada-2025.pdf",
    "career_url": "https://www.uide.edu.ec/comunicacion-y-medios-digitales-en-linea/"
    },
    {
    "career_name": "Comunicación y Medios Digitales",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2024/09/nueva-malla-31-comunicacion-y-medios-digitales-2-1.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-comunicacion-y-medios-digitales/"
    },
    {
    "career_name": "Comercio Exterior y Aduanas (En Línea)",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2025/07/malla-comercio-exterior-y-aduanas.pdf",
    "career_url": "https://www.uide.edu.ec/comercio-exterior-y-aduanas-en-linea/"
    },
    {
    "career_name": "Comercio Exterior y Aduanas",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2025/02/malla-comercio-exterior-y-aduanas-gye.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-comercio-exterior-y-aduanas/"
    },
    {
    "career_name": "Ciencias Políticas y Relaciones Internacionales",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2024/09/nueva-malla-relaciones-internacionales-uio-31-1.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-ciencias-politicas-y-relaciones-internacionales/"
    },
    {
    "career_name": "Ingeniería Civil",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2024/04/malla-ing.-civil-uio-2024.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-ingenieria-civil/"
    },
    {
    "career_name": "Arquitectura",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2024/05/malla-arquitectura-2024.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-arquitectura/"
    },
    {
    "career_name": "Administración Pública (En Línea)",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2026/01/administracion-publica-2025-2.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-administracion-publica-en-linea/"
    },
    {
    "career_name": "Administración de Empresas (En Línea)",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2026/01/admi-empresas.pdf",
    "career_url": "https://www.uide.edu.ec/administracion-de-empresas-online/"
    },
    {
    "career_name": "Administración de Empresas",
    "study_plan_pdf": "https://www.uide.edu.ec/wp-content/uploads/2024/05/malla-adm.-de-empresas-2024.pdf",
    "career_url": "https://www.uide.edu.ec/carrera-de-administracion-de-empresas/"
    }
]

# ======================================================
# 4. FUNCIONES (NO SE MODIFICAN)
# ======================================================
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
- materias (lista con: nombre, semestre)
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

# ======================================================
# 5. MAIN (🔥 SOLO CAMBIÓ LA FUENTE DE DATOS 🔥)
# ======================================================
def main():
    print("📂 Procesando mallas pendientes manuales")

    resultado_final = []

    for i, item in enumerate(MALLAS_PENDIENTES, 1):
        carrera = item.get("career_name")
        url_pdf = item.get("study_plan_pdf")

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
            "universidad": datos_ia.get("universidad") or "Universidad Internacional del Ecuador",
            "carrera": carrera,
            "career_url_ref": item.get("career_url"),
            "pensum": datos_ia.get("pensum"),
            "materias": datos_ia.get("materias", []),
            "totales": datos_ia.get("totales", {})
        })

        limpiar_temporales()

    archivo_salida = OUTPUT_DIR / "uide_mallas_pendientes.json"
    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=4, ensure_ascii=False)

    print("\n✅ PROCESO FINALIZADO")
    print("📁 Archivo creado en:", archivo_salida)

# ======================================================
# 6. ENTRY POINT
# ======================================================
if __name__ == "__main__":
    main()
