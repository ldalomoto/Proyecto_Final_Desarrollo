import google.generativeai as genai
import json
import os
import PIL.Image  # Necesitarás instalar Pillow: pip install Pillow

# 1. CONFIGURACIÓN
API_KEY = "AIzaSyBJCx-SJQCaLPwCPna2c5zY5z5jM53Gy_E"
genai.configure(api_key=API_KEY)

def procesar_imagen_con_ia(ruta_imagen):
    # Cargamos la imagen usando PIL
    try:
        img = PIL.Image.open(ruta_imagen)
    except Exception as e:
        return {"error": f"No se pudo abrir la imagen: {e}"}

    # Inicializamos el modelo (Flash es excelente para visión y rápido)
    model = genai.GenerativeModel(
        model_name='gemini-3-flash-preview', # O gemini-2.0-flash-exp para mayor potencia
        generation_config={"response_mime_type": "application/json"}
    )

    prompt = """
    Analiza visualmente esta imagen de una malla curricular y extrae los datos en formato JSON.
    
    Extrae:
    - universidad (nombre de la institución)
    - carrera (nombre del programa)
    - pensum (año o versión)
    - materias (lista de objetos: codigo, nombre, creditos, horas, semestre)
    - totales (objeto: total_creditos, total_horas)

    Es vital que revises cada semestre visualmente. Si un dato no es legible, pon "null".
    """

    try:
        # Enviamos una lista que contiene el prompt y la imagen
        response = model.generate_content([prompt, img])
        return json.loads(response.text)
    
    except Exception as e:
        return {"error": f"Fallo en la comunicación con la IA: {str(e)}"}

# --- EJECUCIÓN ---
if __name__ == "__main__":
    archivo = "../pdfs/1.jpeg"  # Asegúrate de que la ruta sea correcta
    
    if os.path.exists(archivo):
        print(f"Analizando imagen: {archivo}...")
        resultado = procesar_imagen_con_ia(archivo)
        
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        
        with open("../data_malla/uteq_malla.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=4, ensure_ascii=False)
    else:
        print(f"No se encontró la imagen: {archivo}")