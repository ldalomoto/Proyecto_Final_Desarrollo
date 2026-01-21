import requests
from bs4 import BeautifulSoup
import pdfplumber
import io
import pandas as pd
import time
import os
from urllib.parse import urljoin
import urllib3

# Suprimimos advertencias de seguridad
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración para parecer un navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

class AcademicScraper:
    def __init__(self):
        self.dataset = []

    def extract_text_from_pdf(self, pdf_url):
        """Descarga y extrae texto limpio (SIN ENTERS)"""
        try:
            print(f"      ⬇️ Descargando PDF: {pdf_url}...")
            response = requests.get(pdf_url, headers=HEADERS, timeout=20, verify=False)
            text_content = ""
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content += extracted.replace('\n', ' ') + " "
            return " ".join(text_content.split())
        except Exception as e:
            print(f"      ❌ Error leyendo PDF: {e}")
            return None

    def scrape_uda(self):
        """Estrategia para Universidad del Azuay (UDA)"""
        print("\n--- Iniciando UDA (Universidad del Azuay) ---")
        url_catalogo = "https://www.uazuay.edu.ec/estudios-de-grado"
        
        try:
            resp = requests.get(url_catalogo, headers=HEADERS, timeout=20, verify=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            links = soup.find_all('a', href=True)
            urls_vistas = set() 
            
            for link in links:
                href = link['href']
                texto = link.text.strip()
                
                if "/carreras/" in href and len(texto) > 5:
                    full_link = urljoin(url_catalogo, href)
                    
                    if full_link in urls_vistas: continue
                    urls_vistas.add(full_link)
                    
                    print(f"   🔎 Analizando UDA: {texto}")
                    self._deep_dive_uda(full_link, texto)
                    
        except Exception as e:
            print(f"Error crítico en UDA: {e}")

    def _deep_dive_uda(self, url, career_name):
        try:
            resp = requests.get(url, headers=HEADERS, verify=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            contenido_final = ""
            origen = "HTML"
            
            # --- FASE 1: PDF (Plan A) ---
            pdf_encontrado = False
            for a in soup.find_all('a', href=True):
                if a['href'].lower().endswith('.pdf') and ("malla" in a.text.lower() or "curricular" in a.text.lower()):
                    link_pdf = urljoin(url, a['href'])
                    texto_pdf = self.extract_text_from_pdf(link_pdf)
                    if texto_pdf and len(texto_pdf) > 100:
                        contenido_final = texto_pdf
                        origen = "PDF"
                        pdf_encontrado = True
                        break
            
            # --- FASE 2: HTML LIMPIO (Plan B - Aquí estaba el error del Excel) ---
            if not pdf_encontrado:
                # 1. LIMPIEZA QUIRÚRGICA: Borramos menús, buscadores y basura antes de leer
                elementos_basura = [
                    'header', 'footer', 'nav', 'form', 'script', 'style', 
                    'div.search-block-form', 'div#navbar', 'div.breadcrumb',
                    '.region-header', '.region-footer'
                ]
                for selector in elementos_basura:
                    for tag in soup.select(selector):
                        tag.decompose() # Borra la etiqueta del HTML
                
                # 2. Extracción del contenido limpio
                # Intentamos ir al bloque principal de contenido de la UDA
                main_content = soup.find('div', class_='region-content') or soup.find('section', id='block-system-main') or soup.body
                
                if main_content:
                    texto_sucio = main_content.get_text(separator=' ')
                    contenido_final = " ".join(texto_sucio.split())
            
            # Guardado
            if len(contenido_final) > 200:
                self.dataset.append({
                    'universidad': 'UDA',
                    'carrera': career_name,
                    'url_origen': url,
                    'url_malla': url if origen == "HTML" else "PDF Descargado",
                    'contenido_malla': contenido_final[:15000]
                })
                print(f"      ✅ Datos extraídos ({origen}) - Limpios")
            else:
                print("      ⚠️ Contenido insuficiente.")
                
        except Exception as e:
            print(f"Error navegando carrera UDA {career_name}: {e}")

    def save_data(self):
        df = pd.DataFrame(self.dataset)
        ruta_documentos = os.path.join(os.path.expanduser("~"), "Documents")
        nombre_archivo = "UDA_Limpio.csv" # Cambié el nombre para que sepas cual es el nuevo
        ruta_completa = os.path.join(ruta_documentos, nombre_archivo)
        
        try:
            df.to_csv(ruta_completa, index=False, encoding='utf-8-sig')
            print(f"\n✅ ¡ÉXITO! Archivo guardado en: {ruta_completa}")
        except Exception as e:
            print(f"\n❌ Error guardando: {e}")
            df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')

# --- EJECUCIÓN ---
if __name__ == "__main__":
    bot = AcademicScraper()
    bot.scrape_uda()
    bot.save_data()
                  
