# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
import trulia_scraper.parsing as parsing
from trulia_scraper.items import TruliaItem, TruliaItemLoader


class TruliaSpider(scrapy.Spider):
    name = 'trulia_sold'
    allowed_domains = ['trulia.com']
    custom_settings = {'FEED_URI': 'data/data_sold.jl', 'FEED_FORMAT': 'jsonlines'}

    def __init__(self, state='CA', city='San_Francisco', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = 'http://trulia.com/sold/{city},{state}/'.format(state=state, city=city)
        self.start_urls = [self.base_url]
        self.le = LinkExtractor(allow=r'^https://www.trulia.com/homes/.+/sold/')

    def parse(self, response):
        pagination = response.css('.paginationContainer').xpath('.//*/text()[contains(., "Results")]').extract_first()
        N = parsing.get_number_of_pages_to_scrape(pagination)
        for url in [response.urljoin("{n}_p/".format(n=n)) for n in range(1, N+1)]:
            yield scrapy.Request(url=url, callback=self.parse_index_page)

    def parse_index_page(self, response):
        for link in self.le.extract_links(response):
            yield scrapy.Request(url=link.url, callback=self.parse_property_page)

    def parse_property_page(self, response):
        l = TruliaItemLoader(item=TruliaItem(), response=response)
        l.add_xpath('address', '//*[@data-role="address"]/text()')
        l.add_xpath('city_state', '//*[@data-role="cityState"]/text()')
        l.add_xpath('neighborhood', '//*[@data-role="cityState"]/parent::h1/following-sibling::span/a/text()')
        details = l.nested_css('.homeDetailsHeading')
        details.add_xpath('overview', './/span[contains(text(), "Overview")]/parent::div/following-sibling::div[1]//li/text()')
        l.add_css('description', '#descriptionContainer *::text')

        price_events = details.nested_xpath('.//*[text() = "Price History"]/parent::*/following-sibling::*[1]/div/div')
        price_events.add_xpath('prices', './div[contains(text(), "$")]/text()')
        price_events.add_xpath('dates', './div[contains(text(), "$")]/preceding-sibling::div/text()')
        price_events.add_xpath('events', './div[contains(text(), "$")]/following-sibling::div/text()')

        taxes = details.nested_xpath('.//*[text() = "Property Taxes and Assessment"]/parent::div')
        taxes.add_xpath('property_tax_assessment_year', './following-sibling::div/div[contains(text(), "Year")]/following-sibling::div/text()')
        taxes.add_xpath('property_tax', './following-sibling::div/div[contains(text(), "Tax")]/following-sibling::div/text()')
        taxes.add_xpath('property_tax_assessment_land', './following-sibling::div/div/div[contains(text(), "Land")]/following-sibling::div/text()')
        taxes.add_xpath('property_tax_assessment_improvements', './following-sibling::div/div/div[contains(text(), "Improvements")]/following-sibling::div/text()')
        taxes.add_xpath('property_tax_assessment_total', './following-sibling::div/div/div[contains(text(), "Total")]/following-sibling::div/text()')
        taxes.add_xpath('property_tax_market_value', './following-sibling::div/div[contains(text(), "Market Value")]/following-sibling::div/text()')

        return l.load_item()
