import requests
from bs4 import BeautifulSoup
import pdfplumber
import io
import pandas as pd
import os
import sys
from urllib.parse import urljoin
import urllib3

# --- 1. CONFIGURACIÓN DE SISTEMA ---
# Esto arregla los errores de caracteres raros en la consola de Windows
sys.stdout.reconfigure(encoding='utf-8')

# Ignorar advertencias de seguridad (SSL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Cabeceras para simular ser un navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive'
}

class AcademicScraper:
    def __init__(self):
        self.dataset = [] 
        if not os.path.exists('data'):
            os.makedirs('data')

    # --- HERRAMIENTAS BÁSICAS ---
    def safe_get(self, url):
        """Descarga segura forzando UTF-8"""
        try:
            response = requests.get(url, headers=HEADERS, timeout=25, verify=False)
            response.encoding = 'utf-8' # Forzar codificación correcta
            return response.text
        except Exception as e:
            print(f"      ❌ Error conexión: {e}")
            return None

    def extract_text_from_pdf(self, pdf_url):
        """Descarga y lee PDFs"""
        try:
            print(f"      ⬇️ Bajando PDF: {pdf_url}...")
            response = requests.get(pdf_url, headers=HEADERS, timeout=30, verify=False)
            text_content = ""
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted: text_content += extracted.replace('\n', ' ') + " "
            return " ".join(text_content.split())
        except: return None

    def _guardar(self, uni, carrera, url_origen, url_malla, texto):
        """Guarda en memoria si hay datos válidos"""
        if texto and len(texto) > 50:
            self.dataset.append({
                'universidad': uni,
                'carrera': carrera,
                'url_origen': url_origen,
                'url_malla': url_malla,
                'contenido_malla': texto[:40000]
            })
            print(f"      ✅ GUARDADO: {carrera[:40]}")

    def finalizar(self):
        """Genera el JSON final"""
        if not self.dataset:
            print(f"⚠️ UTMACH: No se extrajeron datos. Revisa si la web está caída.")
            return
        df = pd.DataFrame(self.dataset)
        ruta = os.path.join("data", "UTMACH.json")
        df.to_json(ruta, orient='records', indent=4, force_ascii=False)
        print(f"\n💾 ÉXITO: {ruta} ({len(df)} carreras guardadas)")

    # --- LÓGICA DE EXTRACCIÓN PROFUNDA ---
    def _analizar_profundo(self, url):
        """Entra a la página de la carrera y busca PDF o Texto"""
        html = self.safe_get(url)
        if not html: return
        soup = BeautifulSoup(html, 'html.parser')

        # Intentar obtener el nombre limpio de la carrera
        h1 = soup.find('h1')
        nombre = h1.text.strip() if h1 else url.split('/')[-2].replace('-', ' ').title()

        content, origin = "", "HTML"

        # 1. Buscar PDF (Prioridad: Mallas Curriculares)
        for a in soup.find_all('a', href=True):
            href_low = a['href'].lower()
            if href_low.endswith('.pdf'):
                # Palabras clave que indican que el PDF es importante
                if any(k in href_low for k in ['malla', 'plan', 'curricu', 'asignatura']) or "malla" in a.text.lower():
                    pdf_link = urljoin(url, a['href'])
                    content = self.extract_text_from_pdf(pdf_link)
                    if content:
                        origin = "PDF"
                        break
        
        # 2. Si no hay PDF, guardar el Texto de la Web
        if not content:
            # Eliminar menús y pies de página para limpiar la basura
            for tag in soup.select('header, footer, nav, script, style, .elementor-location-header'): 
                tag.decompose()
            
            # Buscar el contenido principal (UTMACH usa Elementor)
            main = soup.find('div', class_='elementor-section-wrap') or soup.find('main') or soup.body
            if main:
                content = " ".join(main.get_text(separator=' ').split())

        self._guardar("UTMACH", nombre, url, f"{origin}", content)

    # ==========================================
    # EJECUCIÓN: ESTRATEGIA SITEMAP (BACKDOOR)
    # ==========================================
    def scrape_utmach(self):
        print("\n--- Scrapeando UTMACH (Estrategia Sitemaps XML) ---")
        
        # UTMACH usa WordPress, estos son los mapas donde están las páginas
        sitemaps = [
            "https://utmachala.edu.ec/page-sitemap.xml",
            "https://utmachala.edu.ec/sitemap.xml"
        ]
        
        urls_procesadas = set()

        for sitemap in sitemaps:
            print(f"   🗺️ Leyendo mapa: {sitemap}...")
            xml = self.safe_get(sitemap)
            
            if not xml or len(xml) < 500:
                print("      ❌ Mapa vacío o inaccesible.")
                continue

            # Usamos 'html.parser' porque es más robusto leyendo XMLs sucios
            soup = BeautifulSoup(xml, 'html.parser')
            
            # Buscamos las etiquetas <loc> que contienen las URLs
            locs = soup.find_all('loc')
            print(f"      ✅ Enlaces encontrados: {len(locs)}")

            for tag in locs:
                url = tag.text.strip()
                url_low = url.lower()
                
                # --- FILTROS DE CARRERA ---
                if "utmachala.edu.ec" in url_low:
                    # 1. Palabras Clave (Debe tener al menos una)
                    keywords = ['carrera', 'ingenieria', 'licenciatura', 'medicina', 'enfermeria', 'agronomia', 'economía', 'turismo', 'alimentos', 'civil', 'sistemas', 'aquacultura', 'docencia', 'pedagogia']
                    
                    # 2. Palabras Prohibidas (No debe tener ninguna)
                    basura = ['noticia', 'evento', 'horario', 'matricula', 'bienestar', 'investigacion', 'autoridades', 'transparencia', 'jpg', 'png']

                    if any(k in url_low for k in keywords) and not any(b in url_low for b in basura):
                        if url not in urls_procesadas:
                            print(f"      🎯 Candidata: {url}")
                            self._analizar_profundo(url)
                            urls_procesadas.add(url)
        
        self.finalizar()

if __name__ == "__main__":
    bot = AcademicScraper()
    bot.scrape_utmach()