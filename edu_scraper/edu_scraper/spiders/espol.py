import scrapy
from .base_university import BaseUniversitySpider


class EspolSpider(BaseUniversitySpider):
    name = "espol"
    allowed_domains = ["espol.edu.ec"]
    start_urls = [
        "https://www.espol.edu.ec/es/educacion/grado"
    ]

    university_name = "Escuela Superior Politécnica del Litoral"
    city = "Guayaquil"

    def parse(self, response):
        career_links = response.css("a[href*='/carrera']::attr(href)").getall()

        for link in career_links:
            yield response.follow(link, callback=self.parse_career)
