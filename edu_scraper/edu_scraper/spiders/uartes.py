import scrapy
from .base_university import BaseUniversitySpider

class EspolSpider(BaseUniversitySpider):
    name = "uartes"
    allowed_domains = ["uartes.edu.ec"]
    start_urls = [
        "https://www.uartes.edu.ec/sitio/la-universidad/pregrado/"
    ]

    university_name = "Universidad de las Artes"
    university_type = "Pública"
    university_contact = "https://www.uartes.edu.ec/es/contactos"

    def parse(self, response):
        career_links = response.css("a[href*='https://www.uartes.edu.ec/sitio/la-universidad/pregrado/']::attr(href)").getall()

        for link in career_links:
            yield response.follow(link, callback=self.parse_career)

    def parse_career(self, response):
        item = self.create_base_item(response)

        # =========================
        # IDENTIDAD Y FILTRADO
        # =========================
        raw_name = response.css("h1::text").get()
        career_name = self.clean_text(raw_name)

        if not career_name or "licenciatura" not in career_name.lower():
            self.logger.info(f"Omitiendo: {career_name}")
            return

        item["career_name"] = career_name
        item["faculty_name"] = self.clean_text(
            response.css(".field--name-field-facultad::text").get()
        )
        item["degree_title"] = self.clean_text("Licenciado/a")

        # =========================
        # INFORMACIÓN GENERAL
        # =========================
        description_parts = response.css(".elementor-widget-text-editor .elementor-widget-container p::text").getall()
        item["description"] = self.clean_text(" ".join(description_parts))
        
        item["locations"] = ["Guayaquil"]
        item["cost"] = 0

        # CONTACTO ESPECÍFICO DE LA CARRERA
        # Extraemos el texto del enlace mailto
        specific_email = response.css('a[href^="mailto:"]::text').get()
        item["university_contact"] = self.clean_text(specific_email) if specific_email else self.university_contact

        # =========================
        # INFORMACIÓN ACADÉMICA
        # =========================
        item["semesters"] = self.clean_text("Desconocido")
        
        item["modality"] = self.clean_text("Presencial")

        # Enlace del PDF (data-downloadurl)
        item["study_plan_pdf"] = response.css(
            "a.wpdm-download-link::attr(data-downloadurl)"
        ).get()

        yield item