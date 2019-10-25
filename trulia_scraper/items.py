# -*- coding: utf-8 -*-
from scrapy.loader.processors import TakeFirst, Identity, Compose, Join
import scrapy
from trulia_scraper.parsing import *

class overview_item(scrapy.Item):
    url = scrapy.Field(
        output_processor=Compose(TakeFirst())
    )
    address = scrapy.Field(
        output_processor=Compose(TakeFirst())
    )
    city_state = scrapy.Field(
        output_processor=Compose(TakeFirst())
    )
    price = scrapy.Field(
        output_processor=Compose(TakeFirst(),get_number_from_string)
    )  # for items on sale only
    area = scrapy.Field(
        output_processor=Compose(TakeFirst(), get_number_from_string)
    )
    bedrooms = scrapy.Field(
        output_processor=Compose(TakeFirst(), float)
    )
    bathrooms = scrapy.Field(
        output_processor= Compose(TakeFirst(), float)
    )
    year_built = scrapy.Field(
        output_processor=Compose(TakeFirst(), int)
    )
    lot_size = scrapy.Field(
        output_processor=Compose(TakeFirst(), get_number_from_string)
    )
    lot_size_units = scrapy.Field(
        output_processor=Compose(TakeFirst())
    )
    price_per_square_foot = scrapy.Field(
        output_processor=Compose(TakeFirst(), get_number_from_string)
    )
    days_on_Trulia = scrapy.Field(
        output_processor=Compose(TakeFirst(), int)
    )

class basic_info_item(scrapy.Item):
    url = scrapy.Field(
        output_processor=Compose(TakeFirst())
    )
    address = scrapy.Field(
        output_processor=Compose(TakeFirst())
    )
    city_state = scrapy.Field(
        output_processor=Compose(TakeFirst())
    )
    price = scrapy.Field(
        output_processor=Compose(TakeFirst(), get_number_from_string)
    )  # for items on sale only
    area = scrapy.Field(
        output_processor=Compose(TakeFirst(), get_number_from_string)
    )
    bedrooms = scrapy.Field(
        output_processor=Compose(TakeFirst(), float)
    )
    bathrooms = scrapy.Field(
        output_processor=Compose(TakeFirst(), float)
    )


class price_item(scrapy.Item):
    prices = scrapy.Field(
        output_processor= Identity()
    )
    dates = scrapy.Field(
        output_processor= Compose(remove_empty)
    )
    events = scrapy.Field(
        output_processor= Compose(remove_empty)
    )

class taxes_item(scrapy.Item):
    property_tax_assessment_year = scrapy.Field(
        output_processor=Compose(TakeFirst(), int)
    )
    property_tax = scrapy.Field(
        output_processor=Compose(TakeFirst(), get_number_from_string)
    )
    property_tax_assessment_land = scrapy.Field(
        output_processor=Compose(TakeFirst(), get_number_from_string)
    )
    property_tax_assessment_improvements = scrapy.Field(
        output_processor=Compose(TakeFirst(), get_number_from_string)
    )
    property_tax_assessment_total = scrapy.Field(
        output_processor=Compose(TakeFirst(), get_number_from_string)
    )

class price_trends_item(scrapy.Item):
    item1 = scrapy.Field(
        output_processor=Compose(Join())
    )
    item2 = scrapy.Field(
        output_processor=Compose(Join())
    )
    item3 = scrapy.Field(
        output_processor=Compose(Join())
    )


class TruliaItem(scrapy.Item):
    overview = scrapy.Field()
    local_information = scrapy.Field() #todo

    description = scrapy.Field()
    community_description = scrapy.Field()
    home_detail = scrapy.Field()
    office_hours = scrapy.Field()
    open_house = scrapy.Field()

    price_history = scrapy.Field()
    similar_homes = scrapy.Field() #todo
    new_listing = scrapy.Field() #todo

    property_taxes = scrapy.Field()
    price_trends = scrapy.Field()
    comparable_sales = scrapy.Field()

    local_commons = scrapy.Field() #todo
    new_homes = scrapy.Field()


