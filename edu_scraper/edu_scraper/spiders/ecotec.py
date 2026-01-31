import scrapy
from .base_university import BaseUniversitySpider

class EcotecSpider(BaseUniversitySpider):
    name = "ecotec"
    allowed_domains = ["ecotec.edu.ec"]
    start_urls = ["https://ecotec.edu.ec/carreras-de-grado/"]

    university_name = "Universidad Tecnológica Ecotec"
    university_type = "Privada"  # Ecotec es privada
    university_contact = "https://ecotec.edu.ec/contactenos/"

    def parse(self, response):
        # Buscamos los botones de 'Oferta académica' específicamente.
        # En tu captura, están dentro de un div con id que empieza por 'brxe-'
        # Filtramos por texto "Oferta académica" para no traer basura.
        all_links = response.css("a.bricks-button")
        
        for link_node in all_links:
            text = link_node.css("::text").get()
            href = link_node.css("::attr(href)").get()

            if href and text and "Oferta académica" in text:
                # Solo entramos si el link apunta a una facultad o tiene el patrón de facultad
                if "/facultad/" in href:
                    self.logger.info(f"Facultad encontrada: {href}")
                    yield response.follow(href, callback=self.parse_faculty)

    def parse_faculty(self, response):
        # Las facultades de Ecotec listan las carreras en bloques. 
        # Buscamos links que contengan '/carrera-' que es su estándar de URL.
        career_links = response.css("a[href*='/carrera/']::attr(href)").getall()
        
        # Si no hay con ese prefijo, buscamos links dentro de la sección de contenido principal
        if not career_links:
            # Buscamos enlaces que no sean redes sociales ni la propia página
            career_links = response.xpath("//main//a[contains(@href, 'ecotec.edu.ec')]/@href").getall()

        unique_links = []
        for link in career_links:
            # LIMPIEZA CRÍTICA: evitar anclajes, nulos o la misma página
            if link and "#" not in link and link != response.url:
                # Evitar que se meta a Facebook/Instagram si se colaron
                if "facebook" not in link and "instagram" not in link:
                    unique_links.append(link)

        for link in list(set(unique_links)):
            yield response.follow(link, callback=self.parse_career)

    def parse_career(self, response):
        item = self.create_base_item(response)

        # =========================
        # IDENTIDAD
        # =========================
        
        # 1. NOMBRE DE LA CARRERA: ID específico brxe-pdilie
        item["career_name"] = self.clean_text(response.css("h3#brxe-pdilie::text").get())

        # 3. TÍTULO QUE OTORGA
        # El valor está en el span con estilo italic dentro del h3 id 'brxe-ijohcw'
        item["degree_title"] = self.clean_text(
            response.css("h3#brxe-ijohcw span::text").get()
        )

        # =========================
        # INFORMACIÓN GENERAL
        # =========================

        # 4. DESCRIPCIÓN
        # image_ca293a.png: párrafo dentro de div id brxe-amunmw
        item["description"] = self.clean_text(
            response.css("#brxe-amunmw p::text").get()
        )

        # 4. SEDES (LOCATIONS): Capturamos los textos de los enlaces dentro del h3 id brxe-sgqteh
        item["locations"] = response.css("h3#brxe-sgqteh a::text").getall() #or ["Samborondón", "Guayaquil"]

        item["cost"] = "Consultar universidad"

        # =========================
        # INFORMACIÓN ACADÉMICA
        # =========================

        # Duración / Semestres (id="brxe-qogdmo")
        # Usamos el punto '.' en el contains para que busque en todo el nodo h3
        item["semesters"] = self.clean_text(
            response.xpath("//h3[contains(., 'Duración')]/span/text()").get()
        )
        
        # 6. MODALIDAD Y DURACIÓN (Extracción del span posterior al texto)
        # Usamos el span que está dentro del h3 después del texto descriptivo
        item["modality"] = self.clean_text(
            response.xpath("//h3[contains(., 'Modalidad')]//span/text()").get()
        )

        # Plan de estudios (PDF) - Restringido a la carpeta de mallas y extensión .pdf
        item["study_plan_pdf"] = response.xpath(
            "//a[contains(@href, '/mallas/') and contains(@href, '.pdf')]/@href"
        ).get()

        # Alternativa en caso de que la URL cambie: buscar por el texto del botón
        if not item["study_plan_pdf"]:
            item["study_plan_pdf"] = response.xpath(
                "//a[.//h3[contains(., 'MALLA')]]/@href"
            ).get()

        # 6. FACULTAD: Captura desde el h3 de cabecera si el meta falló
        item["faculty_name"] = response.meta.get('faculty_name') or self.clean_text(
            response.css("h3.brxe-heading::text").get()
        )

        yield item