import pdfplumber
import google.generativeai as genai
import json
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# =========================
# 1. ENV
# =========================
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ No se encontró GEMINI_API_KEY en el .env")

genai.configure(api_key=API_KEY)

# =========================
# 2. RUTAS
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_JSON = BASE_DIR / "data_UniDream" / "data" / "ecotec_careers.json"
OUTPUT_DIR = BASE_DIR / "data_UniDream" / "data_malla"
TEMP_PDF_DIR = Path(__file__).parent / "temp_pdfs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_PDF_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# 3. UTILIDADES
# =========================
def descargar_pdf(url, nombre):
    ruta = TEMP_PDF_DIR / nombre
    try:
        r = requests.get(url, timeout=30, verify=False)
        r.raise_for_status()
        ruta.write_bytes(r.content)
        return ruta
    except Exception as e:
        print(f"❌ Error descargando PDF: {e}")
        return None

def extraer_texto_pdf(ruta_pdf):
    texto = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for i, page in enumerate(pdf.pages):
            texto += f"\n--- PÁGINA {i+1} ---\n"
            texto += page.extract_text(layout=True) or ""
    return texto

def procesar_con_gemini(texto):
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = f"""
Analiza la siguiente malla curricular universitaria (ECOTEC).

Extrae SOLO lo que realmente exista en el documento.
Si un dato no aparece, usa null (NO inventes).

Devuelve un JSON con esta estructura:

{{
  "universidad": string,
  "carrera": string,
  "pensum": string | null,
  "materias": [
    {{
      "codigo": string | null,
      "nombre": string,
      "creditos": number | null,
      "horas": number | null,
      "semestre": number | null
    }}
  ]
}}

Texto:
{texto}
"""

    response = model.generate_content(prompt)
    return json.loads(response.text)

# =========================
# 4. MAIN
# =========================
def main():
    carreras = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    resultado_final = []

    for idx, carrera in enumerate(carreras, start=1):
        pdf_url = carrera.get("study_plan_pdf")
        if not pdf_url:
            continue

        print(f"📘 ({idx}) Procesando: {carrera['career_name']}")

        nombre_pdf = carrera["career_name"].replace(" ", "_").lower() + ".pdf"
        ruta_pdf = descargar_pdf(pdf_url, nombre_pdf)

        if not ruta_pdf:
            continue

        try:
            texto = extraer_texto_pdf(ruta_pdf)
            datos = procesar_con_gemini(texto)

            resultado_final.append({
                "universidad": datos.get("universidad") or carrera["university_name"],
                "carrera": carrera["career_name"],
                "career_url_ref": carrera["career_url"],
                "pensum": datos.get("pensum") or carrera.get("data_collection_date", "")[:4],
                "materias": datos.get("materias", [])
            })

        except Exception as e:
            print(f"❌ Error IA en {carrera['career_name']}: {e}")

        finally:
            if ruta_pdf.exists():
                ruta_pdf.unlink()

    salida = OUTPUT_DIR / "ecotec_mallas.json"
    salida.write_text(
        json.dumps(resultado_final, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"\n✅ LISTO. Archivo generado en:\n{salida}")

# =========================
# 5. ENTRY
# =========================
if __name__ == "__main__":
    main()
