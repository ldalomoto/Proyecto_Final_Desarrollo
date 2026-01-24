# Sistema de Recomendación de Carreras Universitarias  
### Ecuador

Plataforma de **búsqueda semántica** para recomendación de carreras universitarias en Ecuador, basada en **Web Scraping**, **Procesamiento de Lenguaje Natural (NLP)** y **Embeddings**.

El sistema interpreta consultas en lenguaje natural y devuelve carreras relevantes según similitud semántica, no por coincidencia exacta de palabras.

---

## Objetivo

Facilitar la **orientación vocacional** mediante un motor inteligente que analiza intereses del usuario y los compara con descripciones reales de carreras universitarias.

---

## Tecnologías Utilizadas

- **Web Scraping:** Scrapy  
- **Procesamiento de PDFs:** pdfplumber + Google Gemini (Flash 1.5)  
- **NLP / Embeddings:** sentence-transformers  
- **Modelo:** all-MiniLM-L6-v2  
- **Búsqueda Semántica:** similitud coseno (scikit-learn)

---

## Estructura del Proyecto

```text
PROYECTO_FINAL_DESARROLLO/
├── data/                 # Datos crudos extraídos desde la web
├── data_malla/           # Mallas curriculares procesadas desde PDF
├── data_unificada/       # Información general + malla curricular
├── data_ia_ready/        # Texto narrativo listo para IA
├── embeddings/           # Vectores numéricos (.pkl)
├── edu_scraper/          # Web Scraping (Scrapy)
│   └── spiders/          # Spiders por universidad
├── procesamiento/        # Lógica de IA y búsqueda
│   ├── carreras_con_texto.py
│   ├── create_embeddings.py
│   └── search_careers.py
└── procesarPDF/          # Extracción de texto desde PDFs

```

Flujo del Sistema
1. Extracción de Datos

Spiders personalizados recorren los portales oficiales de universidades como:

```
EPN

Universidad de Cuenca

UDLA

UIDE
```
```
Salida: JSON con descripción, duración, modalidad y enlaces a mallas curriculares.
```

2. Procesamiento de Mallas Curriculares

Cuando la malla está en PDF:

Se descarga el documento

Se extrae el texto

Google Gemini estructura las materias en JSON

```
Salida: data_malla/
```

3. Preparación para IA

Se unifica la información general con la malla curricular y se genera un texto narrativo por carrera:

```
Carrera: Ingeniería en Sistemas  
Universidad: EPN  
Descripción: ...  
Materias: Programación, Bases de Datos, Redes...
```
```
Salida: data_ia_ready/
```

4. Generación de Embeddings

Cada carrera se transforma en un vector numérico de 384 dimensiones, representando su significado semántico.

Archivo generado:

```
embeddings/career_embeddings.pkl
```

Buscador Semántico

Permite consultas en lenguaje natural sin depender de palabras clave exactas.

```
Ejecución
python procesamiento/search_careers.py
```

Ejemplo

Entrada
```
Me gusta la tecnología y la seguridad de datos
```

Salida
```
CIBERSEGURIDAD | UDLA (89.4%)
INGENIERÍA EN SEGURIDAD DE REDES | EPN (85.2%)
```
Instalación y Configuración

Clonar el repositorio

Crear entorno virtual:

```
python -m venv env
source env/bin/activate
```

Instalar dependencias:

```
pip install scrapy sentence-transformers scikit-learn pdfplumber google-generativeai python-dotenv
```

Crear archivo .env:
```
GEMINI_API_KEY=tu_api_key_aqui
```