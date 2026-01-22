import scrapy
from .base_university import BaseUniversitySpider


class EspeSpider(BaseUniversitySpider):
    name = "espe"
    allowed_domains = ["espe.edu.ec"]
    start_urls = [
        "https://www.espe.edu.ec/oferta-academica-espe-presencial/"
    ]

    university_name = "Universidad de las Fuerzas Armadas ESPE"
    city = "Sangolquí"

    def parse(self, response):
        # Todas las columnas que contienen carreras
        columnas = response.css(
            'div[class^="elementor-column elementor-col-50 elementor-inner-column elementor-element"]'
        )

        for col in columnas:
            links = col.css(
                "span.subtext a[href^='https://www.espe.edu.ec/']::attr(href)"
            ).getall()

            for link in links:
                yield response.follow(
                    link,
                    callback=self.parse_career
                )

    def parse_career(self, response):
        item = self.create_base_item(response)

        # =========================
        # DATOS PRINCIPALES
        # =========================

        item["career_name"] = self.clean_text(
            response.css("i.fa::text").get()
        )

        item["faculty"] = self.clean_text(
            response.css(".field--name-field-facultad::text").get()
        )

        item["degree_title"] = self.clean_text(
            response.xpath("//h1[contains(@class,'elementor-heading-title') and contains(text(),'Título')]/text()").get()
        )

        item["description"] = self.clean_text(
            " ".join(
                response.css(".field--name-body p::text").getall()
            )
        )

        # =========================
        # INFORMACIÓN ACADÉMICA
        # =========================

        item["duration"] = self.clean_text(
            response.xpath(
                "//div[contains(text(),'Duración')]/following-sibling::div/text()"
            ).get()
        )

        item["modality"] = self.clean_text(
            response.xpath(
                "//div[contains(text(),'Modalidad')]/following-sibling::div/text()"
            ).get()
        )

        # =========================
        # FUTURAS EXTENSIONES
        # =========================

        item["mission"] = self.clean_text(
            response.xpath(
                "/html/body/div[2]/main/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[1]/div/div/p[2]/text()"
            ).get()
        )
        item["vision"] = None
        item["objectives"] = None
        item["career_profile"] = None
        item["study_plan_pdf"] = None

        yield item
