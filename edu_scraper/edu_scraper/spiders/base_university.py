import scrapy
from datetime import datetime
from edu_scraper.items import CareerItem


class BaseUniversitySpider(scrapy.Spider):
    university_name = None
    university_type = None
    university_contact = None

    def clean_text(self, text):
        if not text:
            return None
        return " ".join(text.split()).strip()

    def create_base_item(self, response):
        item = CareerItem()

        item["university_name"] = self.university_name
        item["career_url"] = response.url
        item["data_collection_date"] = datetime.now().strftime("%Y-%m-%d")
        item["university_type"] = self.university_type
        item["university_contact"] = self.university_contact

        return item
