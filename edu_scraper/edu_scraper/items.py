import scrapy

class CareerItem(scrapy.Item):
    university = scrapy.Field()
    city = scrapy.Field()
    career_name = scrapy.Field()
    description = scrapy.Field()
    duration = scrapy.Field()
    modality = scrapy.Field()
    url = scrapy.Field()
