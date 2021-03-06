# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
#  -*- coding: utf-8 -*-

import re
import yaml
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from AZ import AZ
from HTTPutils import get_base_url, strip_final_slash, imitate_user, build_search_url
from loggerUtils import init_logging
import logging
import csv
import os
import time



dcap = dict(DesiredCapabilities.PHANTOMJS)  # TODO: split this out into config
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
)


class WalmartScraper(object):
    def __init__(self):
        init_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Job started and logging enabled")

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.yml"), "r") as fh:
            settings = yaml.load(fh)

        self.driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
        self.driver.set_window_size(1024, 768)
        self.shipping_rate = 0.75  # $rate/lb  # TODO: shift this to AZ class
        self.outfile = "../data/test.csv"
        self.fieldnames = ('net', 'roi', 'name', 'price', 'az_price', 'weight',
                           'az_sales_rank', 'az_match', 'url', 'img', 'az_url', 'az_asin')
        self.url_cats = settings['toys']
        self.site_url = settings['site_url']
        self.page_url = settings['page_url']
        self.base_url = strip_final_slash(get_base_url(self.site_url))
        self.az = AZ()
        self.depth_limit = settings['depth_limit']

    def destroy(self):
        """
        method to destroy all objects and clean up.
        :return:
        """
        #self.driver.service.process.send_signal(signal.SIGTERM)
        self.logger.info("Walmart object cleanly destroyed...")
        self.driver.quit()

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

    def get_dollar_amount(self, f):
        if isinstance(f, str):
            f = f.replace(",", "", 1)
            return round(float(re.match(r'\$?(\d+[.]\d\d)', f.strip()).group(1)), 2)
        else:
            return f

    def get_net(self, data):
        az_price = data['az_price']
        if az_price == 0.0:
            return round(0.0,2)
        price = self.get_dollar_amount(data['price'])
        if data['weight'] == "Weight not fetched" or data['weight'] == "Not Available":
            weight = 0.0
        else:
            weight = float(data['weight'])
        try:
            net = (az_price - (price*1.08 + az_price*0.3 + weight*self.shipping_rate))
        except Exception as e:
            net = 0.0
        try:
            net = round(net, 2)
        except:
            self.logger.error("Bad net value for %s - price:%s, az_price:%s, weight:%s" %
                              (data['name'], data['price'], data['az_price'], data['weight']))
            net = 0.0
        return net

    def get_roi(self, data):
        net = self.get_dollar_amount(data['net'])
        price = self.get_dollar_amount(data['price'])
        return round(net/price, 2)

    def get_list(self, page):
        """
        method takes search results page from Walmart and parses out items to save.
        Has error checking for no search results or an empty set.
        :param page: bs4 object returned from get_page
        :return:
        """
        if page.find(string=re.compile(r'We found 0 results')):
            self.run = False
            return
        elif not page.find("ul", {"class": "tile-list-grid"}):
            self.run = False
            return
        else:
            entries = page.find("ul", {"class": "tile-list-grid"})
        for e in entries:
            if len(e) == 1:
                continue
            elif e.name == "script":
                continue
            else:
                imitate_user(0.05)
                entry = {}
                try:
                    entry['name'] = e.find("a", {"class":"js-product-title"}).get_text().strip()
                except:
                    continue
                if 'http://' in e.find("a", {"class":"js-product-title"}).attrs['href']:
                    entry['url'] = e.find("a", {"class":"js-product-title"}).attrs['href']
                else:
                    entry['url'] = "".join((self.base_url, e.find("a", {"class":"js-product-title"}).attrs['href']))
                try:
                    entry['price'] = e.find("span", {"class":"price-display"}).get_text()
                except:
                    continue
                entry['img'] = e.find("img", {"class":"product-image"}).attrs['data-default-image']
                entry['az_price'], entry['weight'], entry['az_sales_rank'], entry['az_match'], entry['az_url'], entry['az_asin'] = self.az.find_best_match(entry['name'], 'Toys')
                entry['net'] = self.get_net(entry)
                entry['roi'] = self.get_roi(entry)
                self.process_output(entry)

    def next_page_url(self, url):
        self.pc += 1
        imitate_user(0.5)
        next_url = url
        if self.page_url:
            next_url += self.page_url
            next_url += str(self.pc)
        if self.pc == self.depth_limit:
            self.run = False  # recursion limit reached
        return next_url

    def get_page(self, url):
        try:
            self.logger.info("Getting %s" % url)
            self.driver.get(url)
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
    # cats = ["/toys/scooters/4171_133073_132589",
    #         "/toys/kids-bikes/4171_133073_1085618",
    #         "/toys/pedal-push/4171_133073_5354",
    #         "/toys/wagons/4171_133073_91644"]
    # for cat in cats:
    scraper = WalmartScraper()
    scraper.init_output()
    # scraper.scrape(0, cat)
    for cat in scraper.url_cats:
        scraper.scrape(0, cat)
    scraper.destroy()
    #time.sleep(10)  # allow phantomjs to tear down
