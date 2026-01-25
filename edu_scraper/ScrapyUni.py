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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive'
}

def clean_text(text):
    if not text: return ""
    return " ".join(text.strip().split())

def scrape_utmach_v3():
    print("--- Iniciando Scraping UTMACH V3 (Rastreador de Home) ---")
    
    if not os.path.exists('data'):
        os.makedirs('data')

    UNI_DATA = {
        "nombre_universidad": "Universidad Técnica de Machala",
        "siglas": "UTMACH",
        "ubicacion": "Machala",
        "tipo": "Pública",
        "contacto": "comunicacion@utmachala.edu.ec",
        "costo": "Gratuita (sujeta a Ley de Gratuidad)"
    }

    base_url = "https://utmachala.edu.ec"
    
    careers_data = []
    urls_visitadas = set()

    try:
        print(f"🌍 Conectando a la página principal: {base_url}...")
        response = requests.get(base_url, headers=headers, verify=False, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Error crítico: La página devolvió código {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Obtener TODOS los enlaces
        links = soup.find_all('a', href=True)
        print(f"   --> ¡Enlaces encontrados en la portada!: {len(links)}")

        # Palabras clave para detectar carreras
        keywords = [
            'ingenieria', 'licenciatura', 'medicina', 'enfermeria', 'derecho', 
            'economia', 'turismo', 'alimentos', 'agronomia', 'acuicultura', 
            'civil', 'psicologia', 'educacion', 'comunicacion', 'marketing', 
            'contabilidad', 'auditoria', 'trabajo-social', 'artes', 'plastica',
            'pedagogia', 'veterinaria', 'biologia', 'quimica', 'sistemas', 'software'
        ]

        # Palabras para descartar basura
        blacklist = [
            'noticia', 'evento', 'posgrado', 'maestria', 'bienestar', 'investigacion', 
            'biblioteca', 'aseguramiento', 'autoridades', 'directorio', 'transparencia',
            'login', 'campus', 'radio', 'tv', 'admision'
        ]

        count_candidatas = 0

        for link in links:
            href = link['href']
            full_url = href if href.startswith("http") else base_url + href
            text_link = clean_text(link.text).lower()
            url_lower = full_url.lower()
            
            # --- FILTROS ---
            # 1. Validar dominio
            if "utmachala.edu.ec" not in url_lower: continue

            # 2. Debe tener palabra clave en la URL o en el Texto
            tiene_keyword_url = any(k in url_lower for k in keywords)
            tiene_keyword_txt = any(k in text_link for k in keywords)
            
            # 3. No debe ser basura
            es_basura = any(b in url_lower for b in blacklist)

            if (tiene_keyword_url or (tiene_keyword_txt and len(text_link) > 5)) and not es_basura:
                
                # Evitar duplicados y la home misma
                if full_url not in urls_visitadas and full_url != base_url and full_url != base_url+"/":
                    urls_visitadas.add(full_url)
                    count_candidatas += 1
                    print(f"   🔎 Analizando candidata ({count_candidatas}): {full_url}...")

                    try:
                        c_resp = requests.get(full_url, headers=headers, verify=False, timeout=20)
                        c_soup = BeautifulSoup(c_resp.text, 'html.parser')

                        # Limpieza
                        for trash in c_soup.select('header, nav, footer, .sidebar, .widget, .elementor-location-header'): 
                            trash.decompose()
                        
                        body_text = c_soup.get_text(" ", strip=True)

                        # VALIDACIÓN DE CONTENIDO: ¿Es realmente una carrera?
                        # Debe tener palabras como "Título", "Malla", "Perfil", "Duración"
                        es_carrera_real = False
                        if "título" in body_text.lower() or "titulo" in body_text.lower(): es_carrera_real = True
                        if "malla" in body_text.lower() and "perfil" in body_text.lower(): es_carrera_real = True
                        
                        if not es_carrera_real:
                            # print("      🗑️ Descartada (Falta información clave)")
                            continue

                        # --- EXTRACCIÓN ---

                        # 1. NOMBRE
                        h1 = c_soup.find('h1')
                        nombre_carrera = clean_text(h1.text) if h1 else ""
                        
                        if not nombre_carrera or "Facultad" in nombre_carrera:
                            # Intentar sacarlo del título de la página
                            nombre_carrera = c_soup.title.text.split('|')[0].replace("Carrera de", "").strip()

                        # 2. FACULTAD
                        facultad = "No especificada"
                        # Buscar "Facultad de ..."
                        match_fac = re.search(r'(Facultad de [A-Za-zÁÉÍÓÚáéíóúñÑ\s]+)', body_text)
                        if match_fac:
                            facultad = clean_text(match_fac.group(1))
                        else:
                            # Deducción por URL
                            if "agro" in full_url: facultad = "Ciencias Agropecuarias"
                            elif "salud" in full_url or "medicina" in full_url: facultad = "Ciencias Químicas y de la Salud"
                            elif "civil" in full_url or "sistemas" in full_url: facultad = "Ingeniería Civil"
                            elif "sociales" in full_url or "derecho" in full_url: facultad = "Ciencias Sociales"
                            elif "empresarial" in full_url: facultad = "Ciencias Empresariales"

                        # 3. TÍTULO
                        titulo = "No especificado"
                        match_tit = re.search(r'(?:Título|Titulo|Otorga)[:\s]*([A-Za-zÁÉÍÓÚáéíóúñÑ\s\.]+)', body_text, re.IGNORECASE)
                        if match_tit: titulo = clean_text(match_tit.group(1))

                        # 4. DURACIÓN
                        semestres = "No especificado"
                        match_sem = re.search(r'(\d+\s*(?:semestres|niveles|ciclos|periodos))', body_text, re.IGNORECASE)
                        if match_sem: semestres = match_sem.group(1)

                        # 5. MALLA
                        malla = "No encontrada"
                        for a_tag in c_soup.find_all('a', href=True):
                            if a_tag['href'].lower().endswith('.pdf') and ("malla" in a_tag.text.lower() or "curricular" in a_tag.text.lower()):
                                malla = a_tag['href']
                                break
                        if malla != "No encontrada" and not malla.startswith("http"):
                            malla = base_url + malla

                        # 6. DESCRIPCIÓN
                        descripcion = ""
                        # Buscar párrafos significativos
                        paragraphs = c_soup.find_all('p')
                        for p in paragraphs:
                            txt = clean_text(p.text)
                            if len(txt) > 200 and "cookies" not in txt.lower():
                                descripcion = txt[:800]
                                break
                        if not descripcion: descripcion = body_text[:600]

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
                            "modalidad": "Presencial", # UTMACH estándar
                            "enlace_carrera": full_url,
                            "fecha_recoleccion": datetime.now().strftime("%Y-%m-%d"),
                            "contacto_universidad": UNI_DATA["contacto"]
                        }
                        careers_data.append(item)
                        print(f"      ✅ Guardado: {nombre_carrera}")

                    except Exception as e:
                        print(f"      ❌ Error interno: {e}")

    except Exception as e:
        print(f"Error general: {e}")

    # Guardar
    if careers_data:
        file_path = os.path.join("data", "UTMACH_careers.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(careers_data, f, ensure_ascii=False, indent=4)
        print(f"\n💾 ÉXITO: {file_path} generado con {len(careers_data)} carreras.")
    else:
        print("⚠️ No se encontraron carreras. (Si esto falla, la web de UTMACH está bloqueando robots).")

if __name__ == "__main__":
    scrape_utmach_v3()