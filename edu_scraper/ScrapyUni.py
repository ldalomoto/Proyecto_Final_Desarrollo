import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import urllib3

# Configuración
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_text(text):
    if not text: return ""
    return " ".join(text.strip().split())

def deducir_duracion_por_niveles(texto_completo):
    """Cuenta hasta qué nivel/ciclo llega la malla en el texto."""
    niveles_encontrados = []
    # Busca patrones como "Nivel Uno", "Nivel 1", "Ciclo VIII", etc.
    patrones = [
        r'Nivel\s+(Uno|Dos|Tres|Cuatro|Cinco|Seis|Siete|Ocho|Nueve|Diez)',
        r'Nivel\s+(\d+)',
        r'Ciclo\s+(\d+)',
        r'Semestre\s+(\d+)'
    ]
    
    mapa_numeros = {
        'Uno': 1, 'Dos': 2, 'Tres': 3, 'Cuatro': 4, 'Cinco': 5, 
        'Seis': 6, 'Siete': 7, 'Ocho': 8, 'Nueve': 9, 'Diez': 10
    }

    for patron in patrones:
        coincidencias = re.findall(patron, texto_completo, re.IGNORECASE)
        for c in coincidencias:
            if c in mapa_numeros:
                niveles_encontrados.append(mapa_numeros[c])
            elif c.isdigit():
                niveles_encontrados.append(int(c))
    
    if niveles_encontrados:
        max_nivel = max(niveles_encontrados)
        return f"{max_nivel} Ciclos (Deducido)"
    
    return "No especificado"

def scrape_uda():
    print("--- Iniciando Scraping UDA (V4.0 - Deducción Lógica) ---")
    
    if not os.path.exists('data'):
        os.makedirs('data')

    UNI_DATA = {
        "nombre_universidad": "Universidad del Azuay",
        "siglas": "UDA",
        "ubicacion": "Cuenca",
        "tipo": "Privada",
        "contacto": "info@uazuay.edu.ec",
        "costo": "Consultar (Privada - Costo diferenciado)"
    }

    list_url = "https://www.uazuay.edu.ec/estudios-de-grado"
    base_url = "https://www.uazuay.edu.ec"
    
    careers_data = []
    urls_visitadas = set()

    try:
        response = requests.get(list_url, headers=headers, verify=False, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href']
            full_url = href if href.startswith("http") else base_url + href
            
            if "/carreras/" in full_url and full_url not in urls_visitadas:
                urls_visitadas.add(full_url)
                print(f"   Analizando: {full_url}...")
                
                try:
                    c_resp = requests.get(full_url, headers=headers, verify=False, timeout=20)
                    c_resp.encoding = 'utf-8'
                    c_soup = BeautifulSoup(c_resp.text, 'html.parser')
                    
                    # Limpieza básica
                    for trash in c_soup.select('header, nav, footer, .sidebar, .search-form'):
                        trash.decompose()

                    body_text = c_soup.get_text(" ", strip=True)

                    # 1. NOMBRE
                    h1 = c_soup.find('h1')
                    nombre_carrera = clean_text(h1.text) if h1 else "Desconocido"

                    # 2. FACULTAD (Buscamos el enlace 'Conoce la facultad')
                    facultad = "No especificada"
                    # Buscar un enlace que diga "Conoce la facultad" o "Facultad"
                    link_fac = c_soup.find('a', string=re.compile(r'Conoce la facultad', re.I))
                    if link_fac:
                        # A veces el link lleva a /facultades/ciencias-administracion -> extraemos de ahi
                        href_fac = link_fac['href']
                        fac_slug = href_fac.split('/')[-1].replace('-', ' ').title()
                        facultad = fac_slug
                    else:
                        # Busqueda de texto de respaldo
                        match_fac = re.search(r'Facultad de ([A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)', body_text)
                        if match_fac: facultad = clean_text(match_fac.group(1))

                    # 3. TÍTULO
                    titulo = "No especificado"
                    match_tit = re.search(r'(?:Título|Titulación)[:\s]*([A-Za-zÁÉÍÓÚáéíóúñÑ\s\.]+?)(?:Duración|Horario|$)', body_text, re.IGNORECASE)
                    if match_tit:
                        titulo = clean_text(match_tit.group(1))

                    # 4. DURACIÓN (Lógica Deductiva)
                    semestres = "No especificado"
                    # Intento 1: Directo
                    match_dur = re.search(r'Duración[:\s]*(\d+\s*[a-zA-Z]+)', body_text, re.IGNORECASE)
                    if match_dur:
                        semestres = clean_text(match_dur.group(1))
                    else:
                        # Intento 2: Contar niveles
                        semestres = deducir_duracion_por_niveles(body_text)

                    # 5. DESCRIPCIÓN (Recorte de Texto)
                    descripcion = ""
                    # Buscamos el bloque entre "Presentación" o "Perfil profesional"
                    # Regex para capturar texto entre encabezados comunes de UDA
                    match_desc = re.search(r'(?:Presentación|Perfil profesional)(.*?)(?:Campo ocupacional|Plan de estudios|Coordinación)', body_text, re.IGNORECASE | re.DOTALL)
                    if match_desc:
                        texto_sucio = match_desc.group(1)
                        # Limpiamos si hay códigos raros
                        descripcion = clean_text(texto_sucio)[:800]
                    else:
                        # Fallback: buscar el primer párrafo largo
                        for p in c_soup.find_all('p'):
                            if len(p.text) > 150:
                                descripcion = clean_text(p.text)
                                break

                    # 6. MALLA
                    malla = "No encontrada"
                    # Buscar PDF
                    for a_tag in c_soup.find_all('a', href=True):
                        if a_tag['href'].lower().endswith('.pdf') and ("malla" in a_tag.text.lower() or "plan" in a_tag.text.lower()):
                            malla = a_tag['href'] if a_tag['href'].startswith("http") else base_url + a_tag['href']
                            break
                    # Buscar Imagen
                    if malla == "No encontrada":
                        for img in c_soup.find_all('img', src=True):
                            if "malla" in img['src'].lower() and "icon" not in img['src'].lower():
                                malla = img['src'] if img['src'].startswith("http") else base_url + img['src']
                                break
                    # Fallback URL (Si no hay archivo, poner la URL de la carrera como referencia)
                    if malla == "No encontrada":
                        malla = full_url + " (Ver sección Plan de Estudios)"

                    # 7. MODALIDAD
                    modalidad = "Presencial"
                    if "semipresencial" in body_text.lower(): modalidad = "Semipresencial"
                    elif "en línea" in body_text.lower(): modalidad = "En línea"

                    item = {
                        "nombre_carrera": nombre_carrera,
                        "nombre_facultad": facultad,
                        "nombre_universidad": UNI_DATA["nombre_universidad"],
                        "nombre_titulo": titulo,
                        "numero_semestres": semestres,
                        "malla_url": malla,
                        "descripcion_carrera": descripcion,
                        "ubicacion_sedes": [UNI_DATA["ubicacion"]],
                        "tipo_universidad": UNI_DATA["tipo"],
                        "costo": UNI_DATA["costo"],
                        "modalidad": modalidad,
                        "enlace_carrera": full_url,
                        "fecha_recoleccion": datetime.now().strftime("%Y-%m-%d"),
                        "contacto_universidad": UNI_DATA["contacto"]
                    }
                    
                    careers_data.append(item)
                    print(f"      ✅ Guardado: {nombre_carrera}")

                except Exception as e:
                    print(f"      ❌ Error en {full_url}: {e}")

    except Exception as e:
        print(f"Error general: {e}")

    if careers_data:
        file_path = os.path.join("data", "UDA_careers.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(careers_data, f, ensure_ascii=False, indent=4)
        print(f"\n💾 ÉXITO: {file_path} generado con {len(careers_data)} carreras.")

if __name__ == "__main__":
    scrape_uda()