import json
import os
from pathlib import Path

def transformar_formato_mallas(ruta_entrada, ruta_salida):
    if not os.path.exists(ruta_entrada):
        print(f"Error: No se encontró el archivo {ruta_entrada}")
        return

    with open(ruta_entrada, "r", encoding="utf-8") as f:
        datos_originales = json.load(f)

    lista_transformada = []

    for item in datos_originales:
        # Extraemos la parte de la IA
        ia = item.get("datos_malla", {})
        
        # VALIDACIÓN DE SEGURIDAD:
        # Si la IA devolvió una lista [ {...} ], tomamos el primer elemento
        if isinstance(ia, list) and len(ia) > 0:
            ia = ia[0]
        
        # Si después de lo anterior NO es un diccionario, creamos uno vacío para evitar el AttributeError
        if not isinstance(ia, dict):
            ia = {}
        
        # Construimos el nuevo objeto plano
        nuevo_item = {
            "universidad": "Universidad de las Artes",
            "carrera": item.get("career_name", ""),
            "career_url_ref": item.get("url_origen", ""),
            "pensum": ia.get("pensum") or "Vigente",
            "materias": ia.get("materias", []),
            "totales": ia.get("totales", {"total_creditos": 0, "total_horas": 0})
        }
        
        # Limpieza de semestres
        if isinstance(nuevo_item["materias"], list):
            for materia in nuevo_item["materias"]:
                sem = str(materia.get("semestre", ""))
                
                # Conversión de Romanos y Texto a Enteros
                if "VIII" in sem: materia["semestre"] = 8
                elif "VII" in sem: materia["semestre"] = 7
                elif "VI" in sem: materia["semestre"] = 6
                elif "IV" in sem: materia["semestre"] = 4
                elif "V" in sem: materia["semestre"] = 5
                elif "III" in sem: materia["semestre"] = 3
                elif "II" in sem: materia["semestre"] = 2
                elif "I" in sem: materia["semestre"] = 1
                # Si ya es un número (como en tu impresión de consola), aseguramos que sea int
                elif sem.isdigit():
                    materia["semestre"] = int(sem)

        lista_transformada.append(nuevo_item)

    output_path = Path(ruta_salida)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(lista_transformada, f, indent=4, ensure_ascii=False)

    print(f"Transformación completada con éxito en: {output_path}")

if __name__ == "__main__":
    ARCHIVO_ENTRADA = "data_malla/uartes_mallas.json"
    ARCHIVO_SALIDA = "data_malla/uartes_mallas2.json"
    transformar_formato_mallas(ARCHIVO_ENTRADA, ARCHIVO_SALIDA)