# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
import trulia_scraper.parsing as parsing
from trulia_scraper.items import TruliaItem, TruliaItemLoader


class TruliaSpider(scrapy.Spider):
    name = 'trulia'
    allowed_domains = ['trulia.com']
    custom_settings = {'FEED_URI': 'data/data_sold_%(state)s_%(city)s_%(time)s.jl', 'FEED_FORMAT': 'jsonlines'}

    def __init__(self, state='CA', city='San_Francisco', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = state
        self.city = city
        self.start_urls = ['http://trulia.com/{state}/{city}'.format(state=state, city=city)]
        self.le = LinkExtractor(allow=r'^https://www.trulia.com/property')

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

        l.add_value('url', response.url)
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

        listing_information = l.nested_xpath('//span[text() = "LISTING INFORMATION"]')
        listing_information.add_xpath('listing_information', './parent::div/following-sibling::ul[1]/li/text()')
        listing_information.add_xpath('listing_information_date_updated', './following-sibling::span/text()', re=r'^Updated: (.*)')

        public_records = l.nested_xpath('//span[text() = "PUBLIC RECORDS"]')
        public_records.add_xpath('public_records', './parent::div/following-sibling::ul[1]/li/text()')
        public_records.add_xpath('public_records_date_updated', './following-sibling::span/text()', re=r'^Updated: (.*)')

        return l.load_item()
