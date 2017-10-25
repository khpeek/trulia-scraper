# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Identity, Compose
import scrapy


class TruliaItem(scrapy.Item):
    url = scrapy.Field()
    address = scrapy.Field()
    city_state = scrapy.Field()
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


def remove_empty(l):
	'''Remove items which evaluate to False (such as empty strings) from the input list.'''
	return [x for x in l if x]


class TruliaItemLoader(ItemLoader):
	default_input_processor = MapCompose(str.strip)
	default_output_processor = TakeFirst()

	overview_out = Identity()
	description_out = Compose(remove_empty)
	prices_out = Identity()
	dates_out = Compose(remove_empty)
	events_out = Compose(remove_empty)

	listing_information_out = Identity()
	public_records_out = Identity()