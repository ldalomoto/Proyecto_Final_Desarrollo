import scrapy
from .base_university import BaseUniversitySpider


class EspolSpider(BaseUniversitySpider):
    name = "espol"
    allowed_domains = ["espol.edu.ec"]
    start_urls = [
        "https://www.espol.edu.ec/es/educacion/grado"
    ]

    university_name = "Escuela Superior Politécnica del Litoral"
    university_type = "Pública"
    university_contact = "https://www.espol.edu.ec/es/contactos"

    def parse(self, response):
        career_links = response.css("a[href*='/carrera']::attr(href)").getall()

        for link in career_links:
            yield response.follow(link, callback=self.parse_career)

    def parse_career(self, response):
        item = self.create_base_item(response)

        # =========================
        # IDENTIDAD
        # =========================

        item["career_name"] = self.clean_text(
            response.css("h1::text").get()
        )

        item["faculty_name"] = self.clean_text(
            response.css(".field--name-field-facultad::text").get()
        )

        item["degree_title"] = self.clean_text(
            response.xpath(
                "//div[contains(text(),'Título')]/following-sibling::div/text()"
            ).get()
        )

        # =========================
        # INFORMACIÓN GENERAL
        # =========================

        item["description"] = self.clean_text(
            " ".join(response.css(".field--name-body p::text").getall())
        )

        item["locations"] = ["Guayaquil"]  # ESPOL es centralizada

        item["cost"] = "Consultar universidad"

        # =========================
        # INFORMACIÓN ACADÉMICA
        # =========================

        item["semesters"] = self.clean_text(
            response.xpath(
                "//div[contains(text(),'Duración')]/following-sibling::div/text()"
            ).get()
        )

        item["modality"] = self.clean_text(
            response.xpath(
                "//div[contains(text(),'Modalidad')]/following-sibling::div/text()"
            ).get()
        )

        item["study_plan_pdf"] = response.css(
            "a[href$='.pdf']::attr(href)"
        ).get()

        yield item
