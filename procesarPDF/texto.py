import pdfplumber
import google.generativeai as genai
import json
import os

# 1. CONFIGURACIÓN
API_KEY = ""
genai.configure(api_key=API_KEY)

def extraer_texto_pdf(ruta_pdf):
    texto_total = ""
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto_total += f"\n--- PÁGINA {i+1} ---\n"
                # Usar layout=True ayuda a mantener columnas en mallas curriculares
                texto_total += pagina.extract_text(layout=True) or ""
        return texto_total
    except Exception as e:
        return f"Error al leer el PDF: {e}"

def procesar_malla_con_ia(ruta_pdf):
    texto_extraido = extraer_texto_pdf(ruta_pdf)
    
    # Probamos con el nombre del modelo más reciente
    # Si sigue fallando, puedes intentar con 'gemini-1.5-pro'
    model = genai.GenerativeModel(
        model_name='gemini-3-flash-preview',
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = f"""
    Eres un extractor de datos académicos. Tu tarea es convertir el texto de una malla curricular en un JSON estructurado.
    
    Extrae los siguientes campos del texto:
    - universidad (nombre de la institución)
    - carrera (nombre del programa)
    - pensum (año o versión)
    - materias (una lista donde cada objeto tenga: codigo, nombre, creditos, horas, semestre)
    - totales (un objeto con total_creditos y total_horas de toda la carrera)

    Si no encuentras un dato, pon "null". No inventes información.
    
    TEXTO DEL DOCUMENTO:
    {texto_extraido}
    """

    try:
        # Generar contenido
        response = model.generate_content(prompt)
        
        # Con response_mime_type: "application/json", Gemini devuelve el JSON puro
        return json.loads(response.text)
    
    except Exception as e:
        return {"error": f"Fallo en la comunicación con la IA: {str(e)}"}

# --- EJECUCIÓN ---
if __name__ == "__main__":
    archivo = "pdfs/malla_economia.pdf"
    
    if os.path.exists(archivo):
        print(f"Procesando {archivo}...")
        resultado = procesar_malla_con_ia(archivo)
        
        # Mostrar y guardar
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
        with open("resultado_malla.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=4, ensure_ascii=False)
    else:
        print(f"No se encontró el archivo: {archivo}")