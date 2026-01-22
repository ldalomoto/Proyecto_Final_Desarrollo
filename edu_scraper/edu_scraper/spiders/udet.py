import scrapy
import re
import unicodedata
from .base_university import BaseUniversitySpider


class UdetSpider(BaseUniversitySpider):
    name = "udet"
    allowed_domains = ["udet.edu.ec"]
    start_urls = ["https://udet.edu.ec/pa-pregrado/"]

    university_name = "Universidad de Especialidades Turísticas"
    city = "Quito"

    def slugify(self, text):
        text = unicodedata.normalize("NFD", text)
        text = text.encode("ascii", "ignore").decode("utf-8")
        text = re.sub(r"[^\w\s-]", "", text.lower())
        return re.sub(r"[\s_-]+", "-", text).strip("-")

    def parse(self, response):
        career_blocks = response.css(
            "div.et_pb_text_3, "
            "div.et_pb_text_4, "
            "div.et_pb_text_5, "
            "div.et_pb_text_7, "
            "div.et_pb_text_8, "
            "div.et_pb_text_9, "
            "div.et_pb_text_10, "
            "div.et_pb_text_11"
        )

        for block in career_blocks:
            career_name = self.clean_text(
                block.css(".et_pb_text_inner p::text").get()
            )

            if not career_name:
                continue

            slug = self.slugify(career_name)

            if slug == "comunicacion":
                slug = "comunicacion-mf"

            if slug == "gastronomia":
                slug = "520-2"
            career_url = f"https://udet.edu.ec/{slug}/"

            yield scrapy.Request(
                career_url,
                callback=self.parse_career,
                meta={"career_name": career_name}
            )

    def parse_career(self, response):
        item = self.create_base_item(response)

        item["career_name"] = response.meta.get(
            "career_name",
            self.clean_text(response.css(".et_pb_header_content_wrapper p::text").get())
        )

        item["faculty"] = self.clean_text(
            response.css(".field--name-field-facultad::text").get()
        )

        item["degree_title"] = self.clean_text(
            response.css("h1.et_pb_module_header::text").get()
        )

        item["description"] = self.clean_text(
            " ".join(
                response.css(".field--name-body p::text").getall()
            )
        )

        item["duration"] = self.clean_text(
            response.css(".percent p::text").get()
        )

        item["modality"] = self.clean_text(
            response.xpath(
                "//div[contains(text(),'Modalidad')]/following-sibling::div/text()"
            ).get()
        )

        item["mission"] = None
        item["vision"] = None
        item["objectives"] = None
        item["career_profile"] = None
        item["study_plan_pdf"] = None

        yield item
