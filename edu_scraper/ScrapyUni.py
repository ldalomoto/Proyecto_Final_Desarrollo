import requests
from bs4 import BeautifulSoup
import pdfplumber
import io
import pandas as pd
import time
import os
from urllib.parse import urljoin
import urllib3

# --- CONFIGURACIÓN ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

class AcademicScraper:
    def __init__(self):
        self.dataset = [] # Memoria temporal
        if not os.path.exists('data'):
            os.makedirs('data')

    def extract_text_from_pdf(self, pdf_url):
        try:
            print(f"      ⬇️ Descargando PDF: {pdf_url}...")
            response = requests.get(pdf_url, headers=HEADERS, timeout=25, verify=False)
            text_content = ""
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content += extracted.replace('\n', ' ') + " "
            return " ".join(text_content.split())
        except Exception as e:
            print(f"      ❌ Error PDF: {e}")
            return None

    def _guardar_temporal(self, uni, carrera, url_origen, url_malla, texto):
        if texto and len(texto) > 200:
            self.dataset.append({
                'universidad': uni,
                'carrera': carrera,
                'url_origen': url_origen,
                'url_malla': url_malla,
                'contenido_malla': texto[:25000]
            })

    def guardar_y_limpiar(self, nombre_archivo):
        """Guarda la universidad actual en su propio JSON y limpia la memoria."""
        if not self.dataset:
            print(f"⚠️ No hay datos de {nombre_archivo} para guardar.")
            return

        df = pd.DataFrame(self.dataset)
        ruta = os.path.join("data", f"{nombre_archivo}.json")
        
        # Guardamos archivo individual
        df.to_json(ruta, orient='records', indent=4, force_ascii=False)
        print(f"\n💾 ARCHIVO CREADO: {ruta} ({len(df)} carreras)")
        
        # ¡IMPORTANTE! Limpiamos la memoria para la siguiente universidad
        self.dataset = [] 

    # ==========================================
    # 1. UTEQ (Quevedo)
    # ==========================================
    def scrape_uteq(self):
        print("\n--- Scrapeando UTEQ ---")
        base = "https://www.uteq.edu.ec/es/grado/carreras"
        try:
            resp = requests.get(base, headers=HEADERS, verify=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            for link in soup.find_all('a', href=True):
                url = urljoin(base, link['href'])
                if "/carrera/" in url:
                    self._deep_uteq(url, link.text.strip())
        except Exception as e: print(f"Error UTEQ: {e}")
        # AL FINALIZAR UTEQ, GUARDAMOS SU PROPIO ARCHIVO
        self.guardar_y_limpiar("UTEQ")

    def _deep_uteq(self, url, nombre):
        try:
            resp = requests.get(url, headers=HEADERS, verify=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                if "malla" in a.text.lower() or a['href'].endswith('.pdf'):
                    pdf = urljoin(url, a['href'])
                    if pdf.endswith('.pdf'):
                        txt = self.extract_text_from_pdf(pdf)
                        if txt: self._guardar_temporal('UTEQ', nombre, url, pdf, txt)
                        break
        except: pass

    # ==========================================
    # 2. UTB (Babahoyo)
    # ==========================================
    def scrape_utb(self):
        print("\n--- Scrapeando UTB ---")
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
                        # Chequeo manual de duplicados en la lista actual
                        if not any(d['url_malla'] == full for d in self.dataset):
                            print(f"   🔎 UTB: {link.text.strip()[:30]}")
                            raw = self.extract_text_from_pdf(full)
                            if raw: self._guardar_temporal('UTB', link.text.strip(), base, full, raw)
            except: pass
        self.guardar_y_limpiar("UTB")

    # ==========================================
    # 3. UDA (Azuay) - Con Limpieza de HTML
    # ==========================================
    def scrape_uda(self):
        print("\n--- Scrapeando UDA ---")
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
                        self._deep_uda(full, link.text.strip())
        except: pass
        self.guardar_y_limpiar("UDA")

    def _deep_uda(self, url, nombre):
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
                self._guardar_temporal('UDA', nombre, url, f"{origin}", content)
        except: pass

    # ==========================================
    # 4. UMET (Metropolitana)
    # ==========================================
    def scrape_umet(self):
        print("\n--- Scrapeando UMET ---")
        url_base = "https://umet.edu.ec/oferta-academica/"
        try:
            resp = requests.get(url_base, headers=HEADERS, timeout=25, verify=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            processed = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                if "umet.edu.ec" in href and len(link.text) > 8:
                    if any(x in href for x in ['login', 'noticias', 'eventos']): continue
                    if href not in processed:
                        processed.add(href)
                        print(f"   🔎 UMET: {link.text.strip()[:30]}")
                        self._deep_umet(href, link.text.strip())
        except: pass
        self.guardar_y_limpiar("UMET")

    def _deep_umet(self, url, name):
        try:
            resp = requests.get(url, headers=HEADERS, verify=False)
            soup = BeautifulSoup(resp.content, 'html.parser')
            content, origin = "", "HTML"
            
            for a in soup.find_all('a', href=True):
                if "malla" in a.text.lower() or a['href'].endswith('.pdf'):
                    content = self.extract_text_from_pdf(a['href'])
                    if content: 
                        origin = "PDF"
                        break
            
            if not content:
                for tag in soup.select('header, footer, nav, .elementor-location-header'):
                    tag.decompose()
                main = soup.find('div', class_='elementor-section-wrap') or soup.body
                if main: content = " ".join(main.get_text(separator=' ').split())

            if content and len(content) > 300:
                self._guardar_temporal('UMET', name, url, f"{origin}", content)
        except: pass

if __name__ == "__main__":
    bot = AcademicScraper()
    
    # Cada función ahora hace: Scrape -> Guarda Archivo -> Limpia Memoria
    bot.scrape_uteq()
    bot.scrape_utb()
    bot.scrape_uda()
    bot.scrape_umet()
    
    print("\n✅ ¡TODO TERMINADO! Revisa tu carpeta 'data'")