# -*- coding: utf-8 -*-
# @Time    : 19-10-28 上午10:41
# @Author  : RenMeng

# coding=utf-8

# from selenium import webdriver
# url = 'https://www.google.com/recaptcha/api2/demo'
# browser = webdriver.Chrome()
# browser.get(url)
# browser.find_elements_by_tag_name("iframe")[0]


from time import sleep
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import json
from random import choice, randint
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from bs4 import NavigableString

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

reg_property_history_row = re.compile('propertyHistory\-[0-9]+')
reg_offerinsight_row = re.compile('offerInsights\-[0-9]+')
reg_property_urls = re.compile('(/[A-Z][A-Z]/[A-Za-z\-/0-9]+/home/[0-9]+)')
user_agent_header = {
    'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'}


class RedFin():
    def __init__(self):
        self.start_url = 'https://www.redfin.com/zipcode/94043'
        # self.session = requests.Session()
        self.use_selenium = True
        #  proxy option can be set after class object is loaded
        # self.use_proxies = True
        self.output_data = []
        self.property_urls = []
        PROXY = "http://127.0.0.1:8118"  # IP:PORT or HOST:PORT
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        self.driver = webdriver.Chrome(options=chrome_options)

        #  load proxies from file one per line proxy:port format
        # self.proxies = [l.rstrip() for l in open('proxies.txt').readlines()]
        #  make a separate session for each proxy
        # self.sessions = {}
        # for proxy in self.proxies:
        #     self.sessions[proxy] = {
        #         'session': requests.Session(),
        #         'proxy': {'http': 'http://' + proxy,
        #                   'https': 'https://' + proxy}
        #     }
        # load data collected so far in order to avoid needing to scrape
        #  the same data twice
        # try:
        #     self.output_data = json.loads(open('redfin_output.json').read())
        # except:
        #     self.output_data = []

    def rand_sleep(self):
        #  you can set the random sleep time for no browser mode here
        sleep(randint(5, 10))

    def parse_finished_urls(self):
        #  function for removing urls that have already completed
        done_urls_list = set()
        for property_data in self.output_data:
            url = property_data['url'][22:]
            done_urls_list.add(url)
            if url in self.property_urls: self.property_urls.remove(url)
        print(str(len(done_urls_list)) + ' properties already done')
        print(str(len(self.property_urls)) + ' proeprties to go')

    def get_search_results(self):
        page_source = self.request_search_page(self.start_url)
        self.property_urls = reg_property_urls.findall(page_source.replace('\\u002F', '/'))
        self.property_urls = list(set(self.property_urls))
        print('found ' + str(len(self.property_urls)) + ' results')
        self.parse_finished_urls()

    def request_search_page(self, page_url):
        if self.use_selenium:
            self.use_selenium = False
            return self.get_page_selenium(page_url)
        else:
            return self.make_page_request(page_url)

    def get_property_data(self):
        count = 0
        for property_url in self.property_urls:
            webdata = self.get_property_page(property_url)
            count += 1
            open('./result/redfin_output_{:d}.json'.format(count), 'w', encoding='utf-8').\
                write(json.dumps(webdata, indent=4, ensure_ascii=False))
            print('finished page ' + str(count))
            self.output_data.append(webdata)

    def make_page_request(self, property_url):
        self.rand_sleep()
        if self.use_selenium:
            return self.get_page_selenium('https://www.redfin.com' + property_url)
        # elif self.use_proxies:
        #     return self.make_page_request_proxy(property_url)
        else:
            return self.make_page_request_no_proxy('https://www.redfin.com' + property_url)

    def make_page_request_no_proxy(self, property_url):
        #  use a loop to handle various http request errors and retry
        #  if 10 fails reached assume we've been blcoked
        # for i in range(10):
        #     try:
        #         http_response = self.session.get(property_url, headers=user_agent_header, verify=False)
        #         if http_response.status_code == 200: break
        #     except Exception as e:
        #         print(1, 'Request error')
        #     if i == 9: print(1, 'blocked error');exit()
        # return http_response.text
        self.driver.get(property_url)
        return self.driver.page_source

    def make_page_request_proxy(self, property_url):
        #  use a loop to handle various http request errors and retry
        #  if 10 fails reached assume we've been blcoked
        for i in range(10):
            try:
                session = self.sessions[choice(self.proxies)]
                http_response = session['session'].get(property_url, headers=user_agent_header,
                                                       proxies=session['proxy'], verify=False)
                if http_response.status_code == 200: break
            except Exception as e:
                print(2, 'Request error')
            if i == 9: print(2, 'blocked error');exit()
        return http_response.text

    def get_property_page(self, property_url):
        page_source = self.make_page_request(property_url)
        return self.parse_property_page(page_source, property_url)

    def parse_property_page(self, page_source, property_url):
        self.soup = BeautifulSoup(page_source, 'html.parser')
        property_data = OrderedDict()

        # basic_info
        property_data['basic_info'] = OrderedDict()
        property_data['basic_info']['url'] = 'https://www.redfin.com' + property_url
        #  use try catch to handle when a data point is not available
        try:
            property_data['basic_info']['street_address'] = \
                self.soup.find('span', attrs={'class': 'street-address'}).get_text()
        except:
            print('street_address not found')

        try:
            property_data['basic_info']['address_locality'] = \
                self.soup.find('span', attrs={'class': 'citystatezip'}).get_text()
        except:
            print('address_locality not found')

        try:
            property_data['basic_info']['price'] = \
                self.soup.find('div', attrs={'class': 'info-block price'}).find('div').get_text()
        except:
            print('price not found')

        try:
            property_data['basic_info']['beds'] = \
                self.soup.find('div', attrs={'data-rf-test-id': 'abp-beds'}).find('div').get_text()
        except:
            print('beds not found')

        try:
            property_data['basic_info']['baths'] = \
                self.soup.find('div', attrs={'data-rf-test-id': 'abp-baths'}).find('div').get_text()
        except:
            print('baths not found')

        try:
            property_data['basic_info']['sqFt'] = \
                ' '.join([item.get_text() for item in
                          (self.soup.select('span.statsValue') + self.soup.select('span.sqft-label'))])
        except:
            print('sqFt not found')

        try:
            property_data['basic_info']['price_per_sqFt'] = \
                self.soup.find('div', attrs={'data-rf-test-id': 'abp-sqFt'}).\
                    find('div', attrs={"data-rf-test-id": "abp-priceperft"}).get_text()
        except:
            print('price_per_sqFt not found')

        try:
            property_data['basic_info']['redfin estimate'] =\
                self.soup(text=re.compile('Redfin Estimate:'))[0].parent.parent.parent.\
                    next_sibling.get_text()
        except:
            print('redfin estimate not found')

        try:
            property_data['basic_info']['days on Redfin'] = \
                self.soup(text=re.compile('On Redfin'))[0].parent.next_sibling.get_text()
        except:
            print('days on Redfin not found')

        try:
            property_data['basic_info']['year_built'] = \
                self.soup.find('span', attrs={"data-rf-test-id": "abp-yearBuilt"}).\
                    find('span', attrs={'class': 'value'}).get_text()
        except:
            print('year_built not found')

        try:
            property_data['basic_info']['status'] = \
                self.soup.find('span', attrs={"data-rf-test-id": "abp-status"}).\
                    find('span', attrs={'class': 'value'}).get_text()
        except:
            print('status not found')

        # overview
        overview = {}
        try:
            overview['describe'] = self.soup.select('div.house-info')[0].\
                select('div[class*="remarks"]')[0].get_text()
        except:
            overview['describe'] = 'not found'
        details = OrderedDict()
        try:
            for child in self.soup.find('div', attrs={'class': 'keyDetailsList'}).children:
                cells = list(child.children)
                details[cells[0].get_text().strip()] = cells[1].get_text().strip()
        except:
            pass
        overview['detail'] = details
        property_data['overview'] = overview

        # use loops to maintain data structure ina dict
        property_data['property_details'] = OrderedDict()
        try:
            for category in self.soup.find('div', attrs={'class': 'amenities-container'}).children:
                if category.get('class')[0] == 'super-group-title':
                    key = category.contents[0]
                elif category.get('class')[0] == 'super-group-content':
                    property_data['property_details'][key] = OrderedDict()
                    for row in category.find_all('div', attrs={'class': 'amenity-group'}):
                        key2 = row.find('h3').get_text()
                        property_data['property_details'][key][key2] = []
                        for row2 in row.find_all('li'):
                            property_data['property_details'][key][key2].append(row2.get_text())
        except:
            pass

        property_data['propert_history'] = []
        try:
            for row in self.soup.find_all('tr', attrs={'id': reg_property_history_row}):
                data_cells = row.find_all('td')
                history_data_row = OrderedDict()
                history_data_row['date'] = data_cells[0].get_text()
                history_data_row['event & source'] = data_cells[1].get_text()
                history_data_row['price'] = data_cells[2].get_text()
                history_data_row['appreciation'] = data_cells[3].get_text()
                property_data['propert_history'].append(history_data_row)
        except:
            pass


        property_data['school'] = OrderedDict()
        try:
            school_tabs = [item.get_text() for item in self.soup.find('div', attrs={'class':'scrollable tabs'})]
            for tab in school_tabs:
                self.driver.find_element_by_xpath('//button[text()="{}"]'.format(tab)).click()
                self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                school_table = self.soup.select('div.schools-content')[0].select('tr.schools-table-row')
                thead = [item.get_text() for item in school_table[0].find_all('th')]
                tbody = [[item for item in trow.find_all('td')] for trow in school_table[1:]]
                col_num = len(thead)
                tbody = [[row[i].find('div', attrs={'data-tf-test-name', 'school-name'}).get_text()
                          if i == 0 else row[i].get_text() for i in range(col_num)] for row in tbody]
                school_item = [{thead[i]: row[i] for i in range(col_num)} for row in tbody]
                property_data['school'][tab] = school_item
        except:
            pass

        property_data['insights'] = []
        try:
            for item in self.soup.find('div',
                                  attrs={'data-rf-test-id': 'tourInsights'}).select('div.currentTourInsights')[0].children:
                common = OrderedDict()
                common['note'] = item.select('div.note')[0].get_text()
                common['agent-info'] = item.select('div.agent-info')[0].find('div').get_text()
                common['date'] = item.select('div.agent-info')[0].find('span', attrs={'class': 'date'}).get_text()
                property_data['insights'].append(common)
        except:
            pass

        property_data['activity'] = []
        try:
            for item in self.soup.find('div',
                                       attrs={'data-rf-test-id': 'activitySection'}).find_all('td'):
                property_data['activity'].append(' '.join([child.get_text() for child in item.select('div.labels')[0].contents]))
        except:
            pass

        property_data['public-facts'] = OrderedDict()
        try:
            for child in self.soup.select('div.public-records-taxes')[0].children:
                key = child.find('h3').get_text()
                property_data['public-facts'][key] = OrderedDict()
                for tr in child.find_all('tr'):
                    cells = list(tr.children)
                    property_data['public-facts'][key][cells[0].get_text()] = cells[1].get_text()
            property_data['public-facts']['home-facts'] = OrderedDict()
            for child in self.soup.select('div.facts-table')[0].select('div.table-row'):
                cells = list(child.contents)
                property_data['public-facts']['home-facts'][cells[0].get_text()] = cells[1].get_text()
        except:
            pass

        try:
            for child in self.soup.select('div.public-records-taxes')[0].children:
                key = child.find('h3').get_text()
                property_data['public-facts'][key] = OrderedDict()
                for tr in child.find_all('tr'):
                    cells = list(tr.children)
                    property_data['public-facts'][key][cells[0].get_text()] = cells[1].get_text()
            property_data['public-facts']['home-facts'] = OrderedDict()
            for child in self.soup.select('div.facts-table')[0].select('div.table-row'):
                cells = list(child.contents)
                property_data['public-facts']['home-facts'][cells[0].get_text()] = cells[1].get_text()
        except:
            pass

        try:
            key = self.soup.select('#redfin-estimate')[0].find('h2').get_text()
            property_data[key] = OrderedDict()
            property_data[key]['EstimateValue'] = self.soup.select('#redfin-estimate')[0].select(
                'div[class*="RedfinEstimateValueHeader"]')[0].get_text()
            property_data[key]['PriceDiff'] = self.soup.select('#redfin-estimate')[0].select(
                'div[class*="listPriceDiff"]')[0].get_text()
            property_data[key]['comps'] = OrderedDict()
            property_data[key]['comps']['based_on'] = self.soup.select('#redfin-estimate')[0].select(
                'div.comps')[0].contents[0].get_text()
            property_data[key]['comps']['homecard'] = []
            for node in self.soup.select('#redfin-estimate')[0].select('div.comps')[0].select(
                    'div.homecard'):
                card = {}
                card['url'] = 'https://www.redfin.com' + node.find('a')['href']
                card['sold_date'] = [item.get_text() for item in node.select('div.topleft')[0]]
                card['details'] = [item.get_text() for item in node.select('div.left')[0]] + \
                                  [item.get_text() for item in node.select('div.right')[0].contents[0].children]
                property_data[key]['comps']['homecard'].append(card)
        except:
            print('redfin-estimate not found')


        # try:
        #     key = self.soup.select('#redfin-estimate')[0].find('h2').get_text()
        #     property_data[key] = OrderedDict()
        # except:
        #     pass

        try:
            key = []
            for child in self.soup.find('div', attrs={'data-rf-test-id': 'neighborhoodSection'}).find('h2').children:
                if isinstance(child, NavigableString):
                    key.append(child)
                else:
                    key += [item.get_text().strip() for item in child.children if item.name != 'script']
            key = ' '.join(key)
            property_data[key] = OrderedDict()
            key2 = self.soup.find('div', attrs={'data-rf-test-id':'neighborhoodSection'}).select(
                'h3[class*="walkscore-header"]')[0].get_text().strip()
            property_data[key][key2] = []
            for child in self.soup.find('div', attrs={'data-rf-test-id': 'neighborhoodSection'}).select(
                    'div.walk-score')[0].select('div.scrollable')[0].contents[0].children:
                property_data[key][key2].append(' '.join([i.get_text() for i in child.children]))
            desc = self.soup.find('div', attrs={'data-rf-test-id':'neighborhoodSection'}).\
                select('div.desc.blurb')[0].get_text()
            property_data[key][key2].append(desc)
            try:
                key3 = self.soup.find('div', attrs={'data-rf-test-id':'neighborhoodSection'}).select(
                    'div.OfferInsights')[0].find('h3').get_text()
                property_data[key][key3] = OrderedDict()
                for tr in self.soup.find('div', attrs={'data-rf-test-id': 'neighborhoodSection'}).select(
                        'div.OfferInsights')[0].find('table', attrs={'class': 'basic-table'}).find_all('tr'):
                    for td in tr.find_all('td'):
                        cell = list(td.children)
                        property_data[key][key3][cell[0].get_text().strip()] = cell[1].get_text().strip()
            except:
                pass

            # 4th
            try:
                key4 = self.soup.find('div', attrs={'data-rf-test-id': 'neighborhoodSection'}).\
                    select('div.title.primary-heading.h3')[0].get_text()
                property_data[key][key4] = []
                for row in self.soup.find('div', attrs={'data-rf-test-id': 'neighborhoodSection'}).\
                        find_all('li', attrs={'id': reg_offerinsight_row}):
                    line = OrderedDict()
                    target_value = ['offer-value', 'sale-date', 'home-stats',
                                    'offer-result-line', 'offer-insight', ]
                    for _v in target_value:
                        try:
                            line[_v] = row.select('div.{}'.format(_v))[0].get_text()
                        except:
                            pass
                    try:
                        line['agent-info'] = row.select('div.agent-info')[0].select('span.agent-detail-name')[0].get_text()
                    except:
                        pass
                    property_data[key][key4].append(line)
            except:
                    pass

            # 5th
            try:
                key5 = self.soup.find('div', attrs={'data-rf-test-id':'neighborhoodSection'}).\
                    select('div.statsAndChartsContainer')[0].find('h3').get_text()
                property_data[key][key5] = []
                table = self.soup.find('div', attrs={'data-rf-test-id':'neighborhoodSection'}).\
                    select('div.statsAndChartsContainer')[0].find('table', attrs={'class': 'basic-table'})
                header = [th.get_text() for th in table.find('thead').find_all('th')]
                header_num = len(header)
                for tr in table.find('tbody').find_all('tr'):
                    line = OrderedDict()
                    value = [td if isinstance(td, NavigableString) else td.get_text()
                             for td in tr.find_all('td')]
                    for i in range(header_num):
                        line[header[i]] = value[i]
                    property_data[key][key5].append(line)

            except:
                pass

        except:
            print('neighborhood info not found')

        try:
            key = 'Nearby Similar Homes'
            property_data[key] = OrderedDict()
            try:
                children = list(self.soup(text=re.compile(key))[1].parent.next_sibling.children)
            except:
                children = list(self.soup(text=re.compile(key))[0].parent.next_sibling.children)

            property_data[key]['desc'] = children[0].get_text()
            property_data[key]['home_list'] = []
            for child in children[1].find_all('div', attrs={'class': 'SimilarHomeCardReact'}):
                home_card = {}
                home_card['url'] = 'https://www.redfin.com' + child.find('a')['href']
                details = []
                try:
                    details.append(child.select('div.topleft')[0].get_text())
                except:
                    pass
                for item in child.select('div.bottomV2')[0].children:
                    if item.name == 'script':
                        continue
                    details += [i if isinstance(i, NavigableString) else i.get_text() for i in item.children]
                print(details)
                home_card['details'] = ' '.join(details)
                property_data[key]['home_list'].append(home_card)
        except:
            print('similar list not found')

        try:
            key = 'Nearby Recently Sold Homes'
            property_data[key] = OrderedDict()
            children = list(self.soup(text=re.compile(key))[0].parent.next_sibling.children)
            property_data[key]['desc'] = children[0].get_text()
            property_data[key]['home_list'] = []
            for child in children[1].find_all('div', attrs={'class': 'SimilarHomeCardReact'}):
                home_card = {}
                home_card['url'] = 'https://www.redfin.com' + child.find('a')['href']
                details = []
                try:
                    details.append(child.select('div.topleft')[0].get_text())
                except:
                    pass
                for item in child.select('div.bottomV2')[0].children:
                    if item.name == 'script':
                        continue
                    details += [i if isinstance(i, NavigableString) else i.get_text() for i in item.children]
                home_card['details'] = ' '.join(details)
                property_data[key]['home_list'].append(home_card)
        except:
            print('recent sold not found')
        print(property_data)
        return property_data

    def use_browser(self):
        self.use_selenium = True
        firefox_profile = FirefoxProfile()
        #  might as well turn off images since we don't need them
        if self.use_proxies:
            #  if use proxies is true load firefox with proxies
            firefox_profile.set_preference("permissions.default.image", 2)
            proxy_host, proxy_port = choice(self.proxies).split(':')
            firefox_profile.set_preference("network.proxy.type", 1)
            firefox_profile.set_preference("network.proxy.http", proxy_host)
            firefox_profile.set_preference("network.proxy.http_port", int(proxy_port))
            firefox_profile.set_preference("network.proxy.ssl", proxy_host)
            firefox_profile.set_preference("network.proxy.ssl_port", int(proxy_port))
        self.driver = Firefox(firefox_profile)
        self.driver.implicitly_wait(2)

    def get_page_selenium(self, page_url):
        self.driver.get(page_url)
        self.selenium_bypass_captcha()
        return self.driver.page_source

    def selenium_bypass_captcha(self):
        #  basic code for handling captcha
        #  this requires the user to actually solve the captcha and then continue
        # try:
        print('do check.....')
        self.driver.switch_to.frame(self.driver.find_elements_by_tag_name("iframe")[0])
        self.driver.find_element_by_class_name('recaptcha-checkbox-border').click()
        print('solve captcha ( pop up only ) and press enter to continue')
        input()
        self.driver.switch_to.default_content()
        self.driver.find_element_by_id('submit').click()
        # except Exception as e:
        #     pass



