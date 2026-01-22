import requests
from bs4 import BeautifulSoup
import pdfplumber
import io
import pandas as pd
import time
import os
from urllib.parse import urljoin
import urllib3

# 1. Configuración anti-bloqueo y seguridad
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

class AcademicScraper:
    def __init__(self):
        self.dataset = []

    def extract_text_from_pdf(self, pdf_url):
        """Descarga y limpia PDF (Elimina ENTERs)"""
        try:
            print(f"      ⬇️ Descargando PDF: {pdf_url}...")
            response = requests.get(pdf_url, headers=HEADERS, timeout=20, verify=False)
            text_content = ""
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        # Reemplazamos \n por espacio
                        text_content += extracted.replace('\n', ' ') + " "
            
            return " ".join(text_content.split())
        except Exception as e:
            print(f"      ❌ Error leyendo PDF: {e}")
            return None

    # --- UNIVERSIDAD 1: UTEQ ---
    def scrape_uteq(self):
        print("\n--- Iniciando UTEQ (Quevedo) ---")
        base_url = "https://www.uteq.edu.ec/es/grado/carreras"
        try:
            resp = requests.get(base_url, headers=HEADERS, verify=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            for link in soup.find_all('a', href=True):
                url = urljoin(base_url, link['href'])
                text = link.text.strip()
                if "/carrera/" in url:
                    print(f"   🔎 UTEQ: {text}")
                    self._deep_dive_uteq(url, text)
        except Exception as e: print(f"Error UTEQ: {e}")

    def _deep_dive_uteq(self, url, career_name):
        try:
            resp = requests.get(url, headers=HEADERS, verify=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                if "malla" in a.text.lower() or a['href'].endswith('.pdf'):
                    full_link = urljoin(url, a['href'])
                    if full_link.endswith('.pdf'):
                        raw = self.extract_text_from_pdf(full_link)
                        if raw: self._add_data('UTEQ', career_name, url, full_link, raw)
                        break
        except: pass

    # --- UNIVERSIDAD 2: UTB ---
    def scrape_utb(self):
        print("\n--- Iniciando UTB (Babahoyo) ---")
        urls = ["http://vice-academico.utb.edu.ec/content-320", "https://www.utb.edu.ec"]
        for base in urls:
            try:
                resp = requests.get(base, headers=HEADERS, timeout=20, verify=False)
                soup = BeautifulSoup(resp.content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    txt = link.text.strip().lower()
                    if href.lower().endswith('.pdf') and ("malla" in txt or "pensum" in txt):
                        full = urljoin(base, href)
                        if not self._is_duplicate(full):
                            print(f"   🎯 UTB Detectada: {txt[:30]}...")
                            raw = self.extract_text_from_pdf(full)
                            if raw: self._add_data('UTB', link.text.strip(), base, full, raw)
            except: pass

    # --- UNIVERSIDAD 3: UDA ---
    def scrape_uda(self):
        print("\n--- Iniciando UDA (Azuay) ---")
        base = "https://www.uazuay.edu.ec/estudios-de-grado"
        try:
            resp = requests.get(base, headers=HEADERS, timeout=20, verify=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            seen = set()
            for link in soup.find_all('a', href=True):
                if "/carreras/" in link['href'] and len(link.text) > 5:
                    full = urljoin(base, link['href'])
                    if full not in seen:
                        seen.add(full)
                        print(f"   🔎 UDA: {link.text.strip()}")
                        self._deep_dive_uda(full, link.text.strip())
        except Exception as e: print(f"Error UDA: {e}")

    def _deep_dive_uda(self, url, name):
        try:
            resp = requests.get(url, headers=HEADERS, verify=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            content, origin = "", "HTML"
            
            # Plan A: PDF
            for a in soup.find_all('a', href=True):
                if a['href'].endswith('.pdf') and "malla" in a.text.lower():
                    content = self.extract_text_from_pdf(urljoin(url, a['href']))
                    if content: 
                        origin = "PDF"
                        break
            
            # Plan B: HTML Limpio
            if not content:
                for tag in soup.select('header, footer, nav, form, script, style, .search-block-form'):
                    tag.decompose()
                
                main = soup.find('div', class_='region-content') or soup.body
                if main:
                    content = " ".join(main.get_text(separator=' ').split())

            if content and len(content) > 200:
                self._add_data('UDA', name, url, f"{origin} Extraction", content)
                print(f"      ✅ Guardado ({origin})")
        except: pass

    # --- UTILIDADES ---
    def _add_data(self, uni, carrera, url_origen, url_malla, texto):
        self.dataset.append({
            'universidad': uni,
            'carrera': carrera,
            'url_origen': url_origen,
            'url_malla': url_malla,
            'contenido_malla': texto[:20000] 
        })

    def _is_duplicate(self, url_malla):
        return any(d['url_malla'] == url_malla for d in self.dataset)

    def save_data(self):
        """Guarda los datos en formato JSON dentro de la carpeta 'data'"""
        if not self.dataset:
            print("⚠️ No hay datos para guardar.")
            return

        # 1. Crear carpeta 'data' si no existe
        folder_path = "data"
        os.makedirs(folder_path, exist_ok=True) # Esto crea la carpeta si falta

        # 2. Definir ruta del archivo JSON
        file_path = os.path.join(folder_path, "mallas_ecuador.json")
        
        # 3. Convertir a DataFrame
        df = pd.DataFrame(self.dataset)

        try:
            # 4. Guardar como JSON
            # orient='records': Crea una lista de objetos [{"u":"...", "c":"..."}, ...]
            # indent=4: Lo hace legible (bonito) para humanos
            # force_ascii=False: Respeta las tildes y ñ (UTF-8 real)
            df.to_json(file_path, orient='records', indent=4, force_ascii=False)
            
            print(f"\n✅ GUARDADO EXITOSO EN JSON: {os.path.abspath(file_path)}")
        except Exception as e:
            print(f"\n❌ Error guardando JSON: {e}")

if __name__ == "__main__":
    bot = AcademicScraper()
    
    # Descomenta las que necesites correr
    # bot.scrape_uteq() 
    # bot.scrape_utb()
    
    # Ejecuta UDA
    bot.scrape_uda()
    
    bot.save_data()