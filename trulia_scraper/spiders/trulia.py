# -*- coding: utf-8 -*-
import os
import re
import scrapy
import math
import datetime
from scrapy.linkextractors import LinkExtractor
from trulia_scraper.items import *
from trulia_scraper.parsing import get_number_from_string
from scrapy.utils.conf import closest_scrapy_cfg
from scrapy.loader import ItemLoader
from utils import get_rel_url
from itertools import zip_longest



class TruliaSpider(scrapy.Spider):
    cols = ['overview', 'local_information', 'description', 'home_detail',
            'community_description', 'office_hours', 'open_house',
            'price_history', 'price_trends', 'property_taxes',
            'new_homes', 'similar_homes', 'new_listing', 'comparable_sales',
            'local_commons']

    name = 'trulia'
    allowed_domains = ['trulia.com']
    custom_settings = {'FEED_URI': os.path.join(os.path.dirname(closest_scrapy_cfg()), 'data/data_for_sale_%(state)s_%(city)s_%(time)s.jl'), 
                       'FEED_FORMAT': 'jsonlines',
                       'FEED_EXPORT_FIELDS': cols}

    def __init__(self, state='CA', city='Mountain_View', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = state
        self.city = city
        # self.start_urls = ['http://trulia.com/{state}/{city}'.format(state=state, city=city)]
        self.start_urls = ['http://trulia.com/{state}/{city}'.format(state=state, city=city)]
        # self.le = LinkExtractor(allow=[r'^https://www.trulia.com/p/ca', r'^https://www.trulia.com/property', r'^https://www.trulia.com/builder-community'])
        self.link_path = '//div[@data-testid="search-result-list-container"]//a/@href'

    def parse(self, response):
        print(response.url, response.status)
        N = self.get_number_of_pages_to_scrape(response)
        self.logger.info("Determined that property pages are contained on {N} different index pages, each containing at most 30 properties. Proceeding to scrape each index page...".format(N=N))
        for url in [response.urljoin("{n}_p/".format(n=n)) for n in range(1, N+1)]:
            yield scrapy.Request(url=url, callback=self.parse_index_page)

    @staticmethod
    def get_number_of_pages_to_scrape(response):
        pagination = response.xpath(
            '//div[@data-testid="pagination-caption"]/text()').extract()
        if len(pagination) > 0:
            pagination = pagination[0]
        pattern = '^1-30 of ([\d,]+) Results$'
        number_of_results = int(re.findall(pattern, pagination)[0].replace(',', ''))
        print(number_of_results)
        return math.ceil(number_of_results/30)

    def parse_index_page(self, response):
        # print(len(self.le.extract_links(response)))
        # for link in self.le.extract_links(response):
        #     yield scrapy.Request(url=link.url, callback=self.parse_property_page)
        for url in response.xpath(self.link_path).extract():
            yield scrapy.Request(url=get_rel_url(response.url, url), callback=self.parse_property_page)

    def parse_property_page(self, response):
        # overview
        il = ItemLoader(item=overview_item(), response=response)
        il.add_value('url', response.url)
        overview_node = il.nested_xpath('//div[@data-testid="home-details-summary-container"]')
        overview_node.add_xpath('address', './/span[@data-testid="home-details-summary-headline"]/text()')
        overview_node.add_xpath('city_state',
                     './/span[@data-testid="home-details-summary-city-state"]/text()')
        overview_node.add_xpath('price',
                     './/*[@data-testid="on-market-price-details"]//text()',
                     re=r'\$([\d,]+)')
        overview_node.add_xpath('area', xpath='.//li//text()', re=r'^([\d,]+)\s?sqft$')
        overview_node.add_xpath('bedrooms', xpath='.//li//text()', re=r'(\d+\.?\d?) (?:Beds|Bed|beds|bed)$')
        overview_node.add_xpath('bathrooms', xpath='.//li//text()', re=r'(\d+\.?\d?) (?:Baths|Bath|baths|bath)$')

        details = il.nested_xpath('//div[@data-testid="features-container"]')
        details.add_xpath('year_built', xpath='.//li//text()', re='Built in (\d+)')
        details.add_xpath('lot_size', xpath='.//li//text()', re=r'Lot Size: ([\d,.]+) (?:acres|sqft)$')
        details.add_xpath('lot_size_units', xpath='.//li//text()', re=r'Lot Size: [\d,.]+ (acres|sqft)$')
        details.add_xpath('price_per_square_foot', xpath='.//li//text()', re=r'\$([\d,.]+)/sqft$')
        details.add_xpath('days_on_Trulia', xpath='.//li//text()', re=r'([\d,]+)\+? Days on Trulia$')
        overview_dict = il.load_item()

        # local info
        local_info_list = response.xpath(
            '(//*[div="Local Information"]/parent::div)[2]/following-sibling::div/div/div//text()').extract()
        # for i in range(len(local_info_list) - 1, -1, -1):
        #     if "Map View" in local_info_list[i] or "Street View" in local_info_list[i]:
        #         local_info_list.remove(local_info_list[i])
        local_dict_values = '\n'.join(local_info_list)

        # price_history
        il = ItemLoader(item=price_item(), response=response)
        table_xpath = '//div[contains(text(), "Price History for")]/../../following-sibling::table'
        il.add_xpath('dates', table_xpath + '//tr[1]/td[1]//text()')
        il.add_xpath('prices', table_xpath + '//tr[1]/td[2]//text()')
        il.add_xpath('events', table_xpath + '//tr[1]/td[3]//text()')
        price_dict = il.load_item()


        # tax info
        il = ItemLoader(item=taxes_item(), response=response)
        table_xpath = '//*[div="Property Taxes and Assessment"]/parent::div/following-sibling::table'
        il.add_xpath('property_tax_assessment_year', table_xpath + '//tr[1]/td[1]//text()')
        il.add_xpath('property_tax', table_xpath + '//tr[2]/td[1]//text()')
        il.add_xpath('property_tax_assessment_land', table_xpath + '//tr[4]/td[1]//text()')
        il.add_xpath('property_tax_assessment_improvements', table_xpath + '//tr[5]/td[1]//text()')
        il.add_xpath('property_tax_assessment_total', table_xpath + '//tr[6]/td[1]//text()')
        tax_dict = il.load_item()

        # 有的“可比较”模块不存在
        comparable_path = '//div[contains(text(), "Comparable Sales")]/../../following-sibling::div[3]'
        header = response.xpath(comparable_path + '//th//text()').extract()
        header.append('url')
        num_tr = len(response.xpath(comparable_path + '//tbody/tr'))
        rows = []
        for i in range(1, num_tr+1):
            rows.append(response.xpath((comparable_path + '//tbody/tr[{:d}]//text()').format(i)).extract())
        urls = response.xpath(comparable_path + '//tbody//a/@href').extract()
        urls = [get_rel_url(response.url, url) for url in urls]
        [rows[i].append(urls[i]) for i in range(num_tr)]
        comparable_list = [list(zip(header, row)) for row in rows]

        # price_trends
        il = ItemLoader(item=price_trends_item(), response=response)
        price_trend_node = il.nested_xpath('//*[div="Price Trends"]/parent::div/following-sibling::div[1]')
        price_trend_node.add_xpath('item1', './*[3]//text()')
        price_trend_node.add_xpath('item2', './*[4]//text()')
        price_trend_node.add_xpath('item3', './*[5]//text()')
        price_trends_dict = il.load_item()
        price_trends = '\n'.join(list(price_trends_dict.values()))

        # local common
        total_reviews = []
        reviews = []
        review_count = response.xpath('count(//div[@data-testid="wls-responisve-slider"]/div/div/child::node())').extract()[0]
        review_count = int(float(review_count))
        for i in range(1, 1 + review_count):
            reviews.append(' '.join(
                response.xpath('//div[@data-testid="wls-responisve-slider"]/div/div/*[{:d}]//text()'.format(i)).extract()))
        reviews = '\n'.join(reviews)
        common_count = response.xpath('count(//div[@data-testid="what-locals-say"]/child::node())').extract()[0]
        common_count = int(float(common_count))
        for i in range(1, common_count):
            total_reviews.append(' '.join(
                response.xpath('//div[@data-testid="what-locals-say"]/*[{:d}]//text()'.format(i)).extract()))
        total_reviews.append(reviews)

        #similar_house
        base_xpath = '//*[div="Similar Homes You May Like"]/parent::div/following-sibling::div[1]/div/div'
        similar_house = self.get_similar_new_part(base_xpath, response)

        # new linking house
        base_xpath = '//div[contains(text(), "New Listings near")]/../../following-sibling::div[1]/div/div'
        new_link_house = self.get_similar_new_part(base_xpath, response)

        # all new homes
        builder_tr_count = response.xpath('count(//table[@data-testid="quick-movein-builder-homes-table"]//tr)').extract()[0]
        builder_tr_count = int(float(builder_tr_count))
        builder_tables = []
        for i in range(1, 1 + builder_tr_count):
            builder_tables.append(response.xpath(
                '//table[@data-testid="quick-movein-builder-homes-table"]//tr[{:d}]/td//text()'.format(i)).extract())

        builder_plans = []
        for i in range(1, 1 + builder_tr_count):
            builder_plans.append(response.xpath(
                '//table[@data-testid="planned-builder-homes-table"]//tr[{:d}]/td//text()'.format(i)).extract())

        new_homes = {}
        if len(builder_tables) > 0:
            new_homes['quick-movein-builder'] = builder_tables
        if len(builder_plans) > 0:
            new_homes['planned-builder'] = builder_plans



        il = ItemLoader(item=TruliaItem(), response=response)
        # home detail
        il.add_xpath('home_detail',
                              '//div[contains(text(), "Home Details for")]/../../following-sibling::ul/li//text()')

        # description
        il.add_xpath('description',
                     '(//*[div="Description"]/parent::div)[2]/following-sibling::div//text()')

        il.add_xpath('community_description',
                     '//div[@data-testid="community-description-text-description-text"]//text()')

        il.add_xpath('office_hours',
                     '//div[@data-testid="office-hours-container"]//text()')

        il.add_xpath('open_house',
                     '//div[@data-testid="open-house-container"]//text()')

        # local_commons

        item = il.load_item()

        # price_history may not exist
        try:
            dates = [datetime.datetime.strptime(date, '%m/%d/%Y') for date in price_dict['dates']]
            prices = [int(price.lstrip('$').replace(',', '')) for price in price_dict['prices']]
            item['price_history'] = sorted(list(zip(dates, prices, price_dict['events'])), key=lambda x: x[0])
        except:
            item['price_history'] = []

        # overview
        item['overview'] = overview_dict

        # property_tax may not exist
        item['property_taxes'] = tax_dict

        #local_view
        item['local_information'] = local_dict_values

        # price_trends
        item['price_trends'] = price_trends

        # comparable_sales
        item['comparable_sales'] = comparable_list

        # local_commons
        item['local_commons'] = total_reviews

        # similar house
        item['similar_homes'] = similar_house

        # new_link house
        item['new_listing'] = new_link_house

        # new homes
        item['new_homes'] = new_homes
        return item

    @staticmethod
    def get_similar_new_part(base_xpath, response):
        result_list = []
        child_num = len(response.xpath(base_xpath + '/child::node()'))
        for i in range(1, child_num):
            il = ItemLoader(item=basic_info_item(), response=response)
            result_list.append(TruliaSpider.get_basic_house_info(il, str(i), response.url,
                                                           base_xpath))
        return result_list


    @staticmethod
    def get_basic_house_info(item_loader, nth, url, base_xpath):
        basic_info = item_loader.nested_xpath(base_xpath)
        basic_info.add_xpath('price', xpath='./*[{}]//text()'.format(nth), re=r'\$([\d,]+)')
        basic_info.add_xpath('area', xpath='./*[{}]//text()'.format(nth), re=r'^([\d,]+)\s?sqft$')
        basic_info.add_xpath('bedrooms', xpath='./*[{}]//text()'.format(nth), re=r'(\d+)\s?(?:Beds|Bed|beds|bed|bd)$')
        basic_info.add_xpath('bathrooms', xpath='./*[{}]//text()'.format(nth), re=r'(\d+\.?\d{0,})\s?(?:Baths|Bath|baths|bath|ba)$')
        basic_info.add_xpath('city_state', xpath='./*[{}]//div[@data-testid="property-street"]/text()'.format(nth))
        basic_info.add_xpath('address', xpath='./*[{}]//div[@data-testid="property-region"]/text()'.format(nth))
        basic_info.add_xpath('url', xpath='./*[{}]//a/@href'.format(nth))
        basic_house = item_loader.load_item()
        basic_house['url'] = get_rel_url(url, basic_house['url'])
        return basic_house