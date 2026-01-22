import scrapy


class CareerItem(scrapy.Item):
    # =========================
    # IDENTIDAD DE LA CARRERA
    # =========================
    career_name = scrapy.Field()
    faculty_name = scrapy.Field()
    university_name = scrapy.Field()
    degree_title = scrapy.Field()

    # =========================
    # INFORMACIÓN ACADÉMICA
    # =========================
    semesters = scrapy.Field()
    modality = scrapy.Field()
    study_plan_pdf = scrapy.Field()

    # =========================
    # INFORMACIÓN GENERAL
    # =========================
    description = scrapy.Field()
    locations = scrapy.Field()          # sedes
    university_type = scrapy.Field()    # pública / privada
    cost = scrapy.Field()
    career_url = scrapy.Field()

    # =========================
    # METADATA
    # =========================
    data_collection_date = scrapy.Field()
    university_contact = scrapy.Field()
