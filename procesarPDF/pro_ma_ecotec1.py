import pdfplumber
import google.generativeai as genai
import json
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

# =========================
# CONFIGURACIÓN GENERAL
# =========================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ No se encontró GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-3-flash"
MAX_REQUESTS = 20   # límite diario real
requests_usadas = 0

BASE_DIR = Path(__file__).resolve().parent
TEMP_PDF_DIR = BASE_DIR / "temp_pdfs"
OUTPUT_FILE = BASE_DIR / "ecotec_mallas1.2.json"

TEMP_PDF_DIR.mkdir(exist_ok=True)

# =========================
# URLS FALTANTES (MANUAL)
# =========================
CARRERAS_FALTANTES = [
    {
    "universidad": "Universidad Tecnológica Ecotec",
    "carrera": "Nutrición y Dietética",
    "career_url_ref": "https://ecotec.edu.ec/facultad/ciencias-de-la-salud-y-desarrollo-humano/carrera/nutricion-y-dietetica/",
    "study_plan_pdf": "https://media.ecotec.edu.ec/docs/grado/mallas/2026/ciencias-de-la-salud/malla-nutricion.pdf"
    },
    {
    "universidad": "Universidad Tecnológica Ecotec",
    "carrera": "Derecho",
    "career_url_ref": "https://ecotec.edu.ec/facultad/derecho-y-gobernabilidad/carrera/derecho/",
    "study_plan_pdf": "https://media.ecotec.edu.ec/docs/grado/mallas/2026/derecho-gobernabilidad/malla-derecho.pdf"
    },
    {
    "universidad": "Universidad Tecnológica Ecotec",
    "carrera": "Fisioterapia",
    "career_url_ref": "https://ecotec.edu.ec/facultad/ciencias-de-la-salud-y-desarrollo-humano/carrera/fisioterapia/",
    "study_plan_pdf": "https://media.ecotec.edu.ec/docs/grado/mallas/2026/ciencias-de-la-salud/malla-fisioterapia.pdf"
    },
    {
    "universidad": "Universidad Tecnológica Ecotec",
    "carrera": "Psicología Clínica",
    "career_url_ref": "https://ecotec.edu.ec/facultad/ciencias-de-la-salud-y-desarrollo-humano/carrera/psicologia-clinica/",
    "study_plan_pdf": "https://media.ecotec.edu.ec/docs/grado/mallas/2026/ciencias-de-la-salud/malla-psicologia.pdf"
    },
    {
    "universidad": "Universidad Tecnológica Ecotec",
    "carrera": "Criminalística",
    "career_url_ref": "https://ecotec.edu.ec/facultad/derecho-y-gobernabilidad/carrera/criminalistica/",
    "study_plan_pdf": "https://media.ecotec.edu.ec/docs/grado/mallas/2026/derecho-gobernabilidad/malla-criminalistica.pdf"
    },
    {
    "universidad": "Universidad Tecnológica Ecotec",
    "carrera": "Negocios Digitales",
    "career_url_ref": "https://ecotec.edu.ec/carreras-de-grado/facultad/carrera/negocios-digitales/",
    "study_plan_pdf": "https://media.ecotec.edu.ec/docs/grado/mallas/2026/ciencias-economicas-empresariales/malla-negocios-digitales.pdf"
    },
    {
    "universidad": "Universidad Tecnológica Ecotec",
    "carrera": "Logística y Transporte",
    "career_url_ref": "https://ecotec.edu.ec/facultad/ciencias-economicas-empresariales/carrera/logistica-y-transporte/",
    "study_plan_pdf": "https://media.ecotec.edu.ec/docs/grado/mallas/2026/ciencias-economicas-empresariales/malla-logistica-transporte.pdf"
    },
    {
    "universidad": "Universidad Tecnológica Ecotec",
    "carrera": "Gestión del Talento Humano",
    "career_url_ref": "https://ecotec.edu.ec/facultad/ciencias-economicas-empresariales/carrera/gestion-del-talento-humano/",
    "study_plan_pdf": "https://media.ecotec.edu.ec/docs/grado/mallas/2026/ciencias-economicas-empresariales/malla-gestion-talento-humano.pdf"
    },
    {
    "universidad": "Universidad Tecnológica Ecotec",
    "carrera": "Negocios Internacionales",
    "career_url_ref": "https://ecotec.edu.ec/facultad/ciencias-economicas-empresariales/carrera/negocios-internacionales/",
    "study_plan_pdf": "https://media.ecotec.edu.ec/docs/grado/mallas/2026/ciencias-economicas-empresariales/malla-negocios-internacionales.pdf"
    }
    # AGREGA MÁS AQUÍ
                ]

# =========================
# FUNCIONES
# =========================
def descargar_pdf(url, nombre):
    ruta = TEMP_PDF_DIR / nombre
    r = requests.get(url, stream=True, verify=False, timeout=20)
    r.raise_for_status()
    with open(ruta, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    return ruta

def extraer_texto_pdf(ruta_pdf):
    texto = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for page in pdf.pages:
            texto += page.extract_text() or ""
    return texto

def llamar_gemini(prompt):
    global requests_usadas

    if requests_usadas >= MAX_REQUESTS:
        raise RuntimeError("⛔ Cuota diaria alcanzada")

    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={"response_mime_type": "application/json"}
    )

    response = model.generate_content(prompt)
    requests_usadas += 1
    return json.loads(response.text)

def cargar_resultados_previos():
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_resultados(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# =========================
# MAIN
# =========================
def main():
    resultados = cargar_resultados_previos()

    for idx, carrera in enumerate(CARRERAS_FALTANTES, start=1):
        try:
            print(f"📘 ({idx}) Procesando: {carrera['carrera']}")

            pdf_path = descargar_pdf(
                carrera["study_plan_pdf"],
                f"{carrera['carrera'].replace(' ', '_')}.pdf"
            )

            texto = extraer_texto_pdf(pdf_path)

            prompt = f"""
Extrae la malla curricular del texto.
Devuelve SOLO JSON con:
universidad, carrera, pensum,
materias (codigo, nombre, creditos, horas, semestre),
totales (total_creditos, total_horas).
Usa null si no existe.
No inventes datos.

TEXTO:
{texto}
"""

            datos = llamar_gemini(prompt)

            resultados.append({
                "universidad": carrera["universidad"],
                "carrera": carrera["carrera"],
                "career_url_ref": carrera["career_url_ref"],
                "pensum": datos.get("pensum"),
                "materias": datos.get("materias", []),
                "totales": datos.get("totales", {})
            })

            guardar_resultados(resultados)
            os.remove(pdf_path)

            print("✅ OK")

        except RuntimeError as e:
            print(str(e))
            print("💾 Progreso guardado. Deteniendo script.")
            break

        except Exception as e:
            print(f"❌ Error en {carrera['carrera']}: {e}")
            continue

    print("🏁 Finalizado")

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    main()
