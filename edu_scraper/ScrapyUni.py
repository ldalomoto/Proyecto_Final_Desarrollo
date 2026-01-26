import time
import json
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def clean_text(text):
    if not text: return ""
    return " ".join(text.strip().split())

def scrape_uce_total():
    print("--- Iniciando Scraping UCE TOTAL (Sin filtro de enlaces / Validación de Contenido) ---")
    
    if not os.path.exists('data'):
        os.makedirs('data')

    chrome_options = Options()
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Lista de facultades
    facultades = [
        {"siglas": "FAU", "url": "https://www.uce.edu.ec/web/fau"},
        {"siglas": "FCA", "url": "https://www.uce.edu.ec/web/fca"},
        {"siglas": "FAG", "url": "https://www.uce.edu.ec/web/fag"},
        {"siglas": "FCE", "url": "https://www.uce.edu.ec/web/fce"},
        {"siglas": "FACSO", "url": "https://www.uce.edu.ec/web/facso"},
        {"siglas": "FIL", "url": "https://www.uce.edu.ec/web/fil"},
        {"siglas": "FING", "url": "https://www.uce.edu.ec/web/fing"},
        {"siglas": "FCM", "url": "https://www.uce.edu.ec/web/fcm"},
        {"siglas": "JURIS", "url": "https://www.uce.edu.ec/web/juris"},
        {"siglas": "FIQ", "url": "https://www.uce.edu.ec/web/fiq"},
        {"siglas": "ODONTO", "url": "https://www.uce.edu.ec/web/fo"},
        {"siglas": "PSICO", "url": "https://www.uce.edu.ec/web/fps"}
    ]

    careers_data = []
    
    # Palabras que indican que NO es una carrera (para ahorrar tiempo)
    skip_keywords = ["noticias", "eventos", "login", "document", "pdf", "jpg", "png", "mail", "transparencia", "rendicion", "horario"]

    for fac in facultades:
        print(f"\n🏛️ Explorando Facultad: {fac['siglas']}...")
        
        try:
            driver.get(fac['url'])
            time.sleep(5) # Dejar que carguen menús dinámicos
            
            soup_index = BeautifulSoup(driver.page_source, 'html.parser')
            all_links = soup_index.find_all('a', href=True)
            
            # FASE 1: RECOLECCIÓN MASIVA
            candidates = set()
            for link in all_links:
                href = link['href']
                
                # Normalizar URL
                full_url = href if href.startswith("http") else "https://www.uce.edu.ec" + href
                
                # Debe ser interna de la UCE y de esta facultad
                if "uce.edu.ec/web/" in full_url and fac['siglas'].lower() in full_url.lower():
                    # No puede ser la home
                    if full_url != fac['url']:
                        # Filtro de basura obvia en la URL
                        if not any(x in full_url.lower() for x in skip_keywords):
                            candidates.add(full_url)
            
            print(f"   --> {len(candidates)} enlaces internos encontrados. Analizando contenido...")

            # FASE 2: VISITA Y VALIDACIÓN
            for i, url in enumerate(candidates):
                try:
                    driver.get(url)
                    # Espera corta, si es texto carga rápido
                    time.sleep(1.5)
                    
                    c_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    body_text = c_soup.get_text(" ", strip=True)
                    body_lower = body_text.lower()

                    # --- EL FILTRO DE VERDAD (CONTENIDO) ---
                    # Para ser carrera, debe tener al menos 2 evidencias académicas
                    evidence = 0
                    if "perfil" in body_lower and "egreso" in body_lower: evidence += 2 # Fuerte indicio
                    if "malla" in body_lower: evidence += 1
                    if "título" in body_lower and "otorga" in body_lower: evidence += 1
                    if "campo" in body_lower and "laboral" in body_lower: evidence += 1
                    if "semestres" in body_lower or "créditos" in body_lower: evidence += 1
                    
                    # Evitar falsos positivos (Autoridades, Historia)
                    if "decano" in body_lower and len(body_text) < 1000: evidence -= 5
                    if "misión" in body_lower and "visión" in body_lower and len(body_text) < 1000: evidence -= 5

                    if evidence >= 2:
                        # 1. NOMBRE REAL
                        # Intentar sacar del H1, o buscar texto grande
                        h1 = c_soup.find('h1') or c_soup.find('h2', class_='header-title')
                        nombre_real = clean_text(h1.text) if h1 else ""
                        
                        # Si el H1 es genérico (Visor), buscar patrón "Carrera de X"
                        if not nombre_real or "visor" in nombre_real.lower() or "bienvenido" in nombre_real.lower():
                            # Buscar en el título de la pestaña del navegador
                            nombre_real = driver.title.split('-')[0].strip()
                        
                        # Limpieza
                        nombre_final = re.sub(r'Carrera de|Licenciatura en|Ingeniería en|Rediseño|Vigente|Inicio|Home', '', nombre_real, flags=re.I).strip()
                        
                        # Si después de limpiar queda vacío o es basura, saltar
                        if len(nombre_final) < 4 or "facultad" in nombre_final.lower(): continue

                        # 2. TÍTULO
                        titulo = "No especificado"
                        mt = re.search(r'(?:Título|Titulo|Otorga)[:\s]*([A-Za-zÁÉÍÓÚáéíóúñÑ\s\.]+)', body_text, re.IGNORECASE)
                        if mt: titulo = clean_text(mt.group(1))

                        # 3. MALLA (PDF Estricto)
                        malla_url = "No encontrada"
                        pdfs = c_soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
                        for p in pdfs:
                            if "malla" in p.text.lower() or "plan" in p.text.lower():
                                malla_url = p['href']
                                if not malla_url.startswith("http"): malla_url = "https://www.uce.edu.ec" + malla_url
                                break
                        
                        # 4. DESCRIPCIÓN
                        desc = ""
                        for p in c_soup.find_all('p'):
                            if len(p.text) > 200:
                                desc = clean_text(p.text)[:600]
                                break

                        # GUARDAR
                        item = {
                            "nombre_carrera": nombre_final,
                            "nombre_facultad": fac['siglas'],
                            "nombre_universidad": "Universidad Central del Ecuador",
                            "nombre_titulo": titulo,
                            "malla_url": malla_url,
                            "descripcion_carrera": desc,
                            "ubicacion_sedes": ["Quito"],
                            "tipo_universidad": "Pública",
                            "enlace_carrera": url,
                            "fecha_recoleccion": datetime.now().strftime("%Y-%m-%d")
                        }

                        # Evitar duplicados exactos
                        if not any(c['enlace_carrera'] == url for c in careers_data):
                            careers_data.append(item)
                            print(f"      ✅ ENCONTRADA: {nombre_final}")

                except Exception:
                    pass

        except Exception as e:
            print(f"   ⚠️ Error en facultad {fac['siglas']}: {e}")

    driver.quit()

    if careers_data:
        file_path = os.path.join("data", "UCE_careers_total.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(careers_data, f, ensure_ascii=False, indent=4)
        print(f"\n💾 RECOPILACIÓN EXITOSA: {len(careers_data)} carreras reales guardadas.")
    else:
        print("⚠️ No se encontraron datos. La web puede ser una SPA muy compleja.")

if __name__ == "__main__":
    scrape_uce_total()