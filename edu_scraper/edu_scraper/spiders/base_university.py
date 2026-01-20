import scrapy
from edu_scraper.items import CareerItem


class BaseUniversitySpider(scrapy.Spider):
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": True
    }

    university_name = ""
    city = ""

    def parse_career(self, response):
        item = CareerItem()

        item["university"] = self.university_name
        item["city"] = self.city
        item["career_name"] = self.clean_text(
            response.css("h1::text").get()
        )

        item["description"] = self.clean_text(
            " ".join(response.css("p::text").getall())
        )

        item["duration"] = self.clean_text(
            response.css(".duration::text").get()
        )

        item["modality"] = self.clean_text(
            response.css(".modality::text").get()
        )
    
        item["url"] = response.url

        yield item

    def clean_text(self, text):
        if not text:
            return None
        return " ".join(text.split())
