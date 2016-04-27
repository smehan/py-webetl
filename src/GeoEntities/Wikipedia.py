# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
#  -*- coding: utf-8 -*-

import re
import yaml
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from HTTPutils import get_base_url, strip_final_slash, imitate_user, build_search_url
from loggerUtils import init_logging
#from Pydb import Mysql
import logging
import csv
import os
import time
import datetime



dcap = dict(DesiredCapabilities.PHANTOMJS)  # TODO: split this out into config
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
)


class WikiScraper(object):
    def __init__(self):
        init_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Wiki Geo object initialized and logging enabled")

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"wiki_config.yml"), "r") as fh:
            settings = yaml.load(fh)

        #self.db = Mysql(settings['db_config'])

        self.driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
        self.driver.set_window_size(1024, 768)
        self.outfile = settings['output']
        self.depth_limit = settings['depth_limit']
        self.debug = settings['debug']
        self.fieldnames = ('net', 'roi', 'title', 'price', 'az_price', 'weight',
                           'az_sales_rank', 'az_match', 'url', 'img', 'az_url', 'az_asin',
                           'item_id')
        self.top_url = settings['top_url']
        self.base_url = strip_final_slash(get_base_url(self.top_url))

    def destroy(self):
        """
        method to destroy all objects and clean up.
        :return:
        """
        #self.driver.service.process.send_signal(signal.SIGTERM)
        #self.logger.info("Database connection closed...")
        #self.db.exit()
        self.logger.info("Wiki object cleanly destroyed...")
        self.driver.quit()

    def start_scrape(self):
        self.run = True  # initialize run
        url = self.top_url
        try:
            page = self.get_page(url)
        except Exception as e:
            self.logger.error("Error with {} and extraction stopped...".format(url))
            return
        topcats = self._build_cats(page, lvl='us')
        statecats = [self._build_cats(self.get_page(c[1]), lvl='state') for c in topcats]
        countycats = self._build_cats(self.get_page() , lvl='county')
 # go get links for each county and return full list. will then build a method to scrape each leaf.

    def _build_cats(self, page, lvl=None):
        """parse all the top level links and build a dictionary of containers to walk
        :param page: page is a bs4 object to parse
        :param lvl: string indicating what level of category container we are at.
        :return: a dict
        """
        if lvl is None:
            self.run = False
            return
        if page.find("div", {"class": "noarticletext"}):
            self.run = False
            return
        elif lvl == 'us':
            block = page.find("div", {"class": "mw-category-group"})  # first block in the container page, which is US
            links = [(e.contents[0].split(" ")[0], "".join((self.base_url, e.attrs['href']))) for e in block.find_all("a", {"class": "CategoryTreeLabel"})]
            return links
        elif lvl == 'state':
            links = []
            block = page.find_all("div", {"class": "CategoryTreeItem"})
            for e in block:
                type, locale = self._parse_link_title(e.a.contents[0])
                links.append((type, locale, "".join((self.base_url, e.a.attrs['href']))))
            return links

    def _parse_link_title(self, text):
        """
        :param text: link text
        :return: components of type, state
        """
        return self._get_place_type(text), self._get_state(text)

    def _get_place_type(self, text):
        """
        parse a string to determine which place type it contains
        :param text: string to parse
        :return:  a place type, e.g. City
        """
        types = [('VILLAGE', 'VILLAGES'), ('UNINC', 'UNINCORPORATED'), ('TOWN', 'TOWNS'),
                 ('HAMLET', 'HAMLETS'), ('CITY', 'CITIES'), ('BORO', 'BOROUGH'),
                 ('HISTORIC', 'FORMER'), ('CDP', 'CENSUS')]
        for t in types:
            if t[1] in text.upper():
                return t[0]
        return None

    def _get_state(self, text):
        """ parse a string to determine which state it contains
        :param text: string to parse
        :return: a state abbreviation
        """
        states = [('AL', 'ALABAMA'), ('AK', 'ALASKA'), ('AR', 'ARKANSAS'), ('AZ', 'ARIZONA'),
                  ('CA', 'CALIFORNIA'), ('CO', 'COLORADO'), ('CT', 'CONNECTICUT'), ('DE', 'DELAWARE'),
                  ('FL', 'FLORIDA'), ('GA', 'GEORGIA'), ('HI', 'HAWAII'), ('ID', 'IDAHO'), ('IL', 'ILLINOIS'),
                  ('IN', 'INDIANA'), ('IA', 'IOWA'), ('KS', 'KANSAS'), ('KY', 'KENTUCKY'), ('LA', 'LOUISIANA'),
                  ('ME', 'MAINE'), ('MD', 'MARYLAND'), ('MA', 'MASSACHUSETTS'), ('MI', 'MICHIGAN'), ('MN', 'MINNESOTA'),
                  ('MS', 'MISSISSIPPI'), ('MO', 'MISSOURI'), ('MT', 'MONTANA'), ('NE', 'NEBRASKA'), ('NV', 'NEVADA'),
                  ('NH', 'NEW HAMPSHIRE'), ('NJ', 'NEW JERSEY'), ('NM', 'NEW MEXICO'), ('NY', 'NEW YORK'), ('NC', 'NORTH CAROLINA'),
                  ('ND', 'NORTH DAKOTA'), ('OH', 'OHIO'), ('OK', 'OKLAHOMA'), ('OR', 'OREGON'), ('PA', 'PENNSYLVANIA'),
                  ('RI', 'RHODE ISLAND'), ('SC', 'SOUTH CAROLINA'), ('SD', 'SOUTH DAKOTA'), ('TN', 'TENNESSEE'), ('TX', 'TEXAS'),
                  ('UT', 'UTAH'), ('VT', 'VERMONT'), ('VA', 'VIRGINIA'), ('WA', 'WASHINGTON'), ('WV', 'WEST VIRGINIA'),
                  ('WI', 'WISCONSIN'), ('WY', 'WYOMING')]
        for s in states:
            if s[1] in text.upper():
                return s[0]
        return None

    def scrape(self, pc=None, change_url=None):
        """
        :param change_url is the changing part of wider site url, if there
        are multiple sections to hit.
        :param pc is an integer indicating where to start with a paginated url.
        """
        self.run = True  # initialization of a site/section.
        if pc is not None:
            self.pc = pc
        while self.run is True:
            url = self.next_page_url(build_search_url(self.site_url, change_url))
            try:
                page = self.get_page(url)
            except Exception as e:
                self.logger.error("Error with %s and skipped" % url)
                continue
            self.get_list(page)
        if change_url is None:
            self.logger.info("Site %s finished" % self.site_url)
        else:
            self.logger.info("Section %s finished" % change_url)

    def init_output(self):
        if not os.path.exists(self.outfile):
            with open(self.outfile, "w", encoding='utf-8') as fh:
                outwriter = csv.DictWriter(fh,
                                           fieldnames=self.fieldnames,
                                           delimiter="\t")
                outwriter.writeheader()

    def process_output(self, data):
        with open(self.outfile, 'a', encoding='utf-8') as fh:
            outwriter = csv.DictWriter(fh,
                                       fieldnames=self.fieldnames,
                                       delimiter="\t")
        outwriter.writerow(data)

    def get_list(self, page):
        """
        method takes page from source and parses out items to save.
        :param page: bs4 object returned from get_page
        :return:
        """
        imitate_user(0.5)
        if page.find(string=re.compile(r'We found 0 results')):
            self.run = False
            return
        elif not page.find("div", {"id": "summary"}):
            self.run = False
            return
        else:
            entries = page.find("div", {"id": "summary"})
        for e in entries:
            if len(e) == 1:
                continue
            elif e.name == "script":
                continue
            else:
                entry = {}
                try:
                    entry['title'] = e.find("a", {"class":"js-product-title"}).get_text().strip()
                except:
                    continue
                if 'http://' in e.find("a", {"class":"js-product-title"}).attrs['href']:
                    entry['url'] = e.find("a", {"class":"js-product-title"}).attrs['href']
                else:
                    entry['url'] = "".join((self.base_url, e.find("a", {"class":"js-product-title"}).attrs['href']))
                try:
                    entry['price'] = e.find("span", {"class":"price-display"}).get_text().replace('$', '')
                except:
                    continue
                entry['img'] = e.find("img", {"class":"product-image"}).attrs['data-default-image']
                entry['item_id'] = e.find("div", {"class": "js-tile", "class": "tile-grid-unit"}).attrs['data-item-id']
                #entry['az_price'], entry['weight'], entry['az_sales_rank'], entry['az_match'], entry['az_url'], entry['az_asin'] = self.az.find_best_match(entry['title'], 'Toys')
                #entry['net'] = self.get_net(entry)
                #entry['roi'] = self.get_roi(entry)
                self.process_output(entry)

    def get_page(self, url):
        try:
            self.logger.info("Getting %s" % url)
            self.driver.get(url)
            # cookie = {'aam_aud': 'dat%3D2950725', 'ttax': 0}
            # self.driver.add_cookie(cookie)
            # self.driver.add_cookie({'angellist': 'df26dbdf4989a9473fb37b4821da9f8b',
            #             'path': '/',
            #             'expires': 'Wed, 23-Mar-2016 00:02:49 GMT'})
            # self.driver.get_cookies()
        except ValueError as e:
            imitate_user(2)
            try:
                self.driver.get(url)
            except:
                raise
        except Exception as e:
            self.logger.error(url, e)
        # try:
        #     wait = WebDriverWait(self.driver, 3)
        #     wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div")))
        # except Exception as e:
        #     self.logger.error("WebDriverWait error")
        page = BeautifulSoup(self.driver.page_source, "lxml")
        return page


if __name__ == '__main__':
    scraper = WikiScraper()
    scraper.init_output()
    scraper.start_scrape()
    scraper.destroy()
