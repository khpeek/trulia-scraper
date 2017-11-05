# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Identity, Compose
import scrapy
from trulia_scraper.parsing import remove_empty, get_number_from_string


class TruliaItem(scrapy.Item):
    url = scrapy.Field()
    address = scrapy.Field()
    city_state = scrapy.Field()
    price = scrapy.Field()              # for items on sale only
    neighborhood = scrapy.Field()
    overview = scrapy.Field()
    description = scrapy.Field()

    # Columns from the 'price events' table are stored in separate lists
    prices = scrapy.Field()
    dates = scrapy.Field()
    events = scrapy.Field()

    # Property tax information is on 'sold' pages only
    property_tax_assessment_year = scrapy.Field()
    property_tax = scrapy.Field()
    property_tax_assessment_land = scrapy.Field()
    property_tax_assessment_improvements = scrapy.Field()
    property_tax_assessment_total = scrapy.Field()
    property_tax_market_value = scrapy.Field()

    # The 'Features' sections is on 'for sale' pages only
    listing_information = scrapy.Field()
    listing_information_date_updated = scrapy.Field()
    public_records = scrapy.Field()
    public_records_date_updated = scrapy.Field()

    # Items generated from further parsing of 'raw' scraped data
    area = scrapy.Field()
    lot_size = scrapy.Field()
    lot_size_units = scrapy.Field()
    price_per_square_foot = scrapy.Field()      # For properties on sale only
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    year_built = scrapy.Field()
    days_on_Trulia = scrapy.Field()
    views = scrapy.Field()
    price_history = scrapy.Field()


class TruliaItemLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    price_out = Compose(TakeFirst(), lambda s: int(s.replace(',', '')))
    overview_out = Identity()
    description_out = Compose(remove_empty)
    prices_out = Identity()
    dates_out = Compose(remove_empty)
    events_out = Compose(remove_empty)

    listing_information_out = Identity()
    public_records_out = Identity()

    area_out = Compose(TakeFirst(), get_number_from_string)
    lot_size_out = Compose(TakeFirst(), get_number_from_string)
    price_per_square_foot_out = Compose(TakeFirst(), get_number_from_string)
    bedrooms_out = Compose(TakeFirst(), int)
    bathrooms_out = Compose(TakeFirst(), int)
    year_built_out = Compose(TakeFirst(), int)
    days_on_Trulia_out = Compose(TakeFirst(), lambda s: int(s.replace(',', '')))
    views_out = Compose(TakeFirst(), lambda s: int(s.replace(',', '')))
