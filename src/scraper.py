# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
#  -*- coding: utf-8 -*-

import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from AZProdSearch import *
from HTTPutils import get_base_url, strip_final_slash, imitate_user, build_search_url
import csv
import os


dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
)

class WalmartScraper(object):
    def __init__(self):

        with open("config.yaml", "r") as f:
            settings = yaml.load(f)

        self.driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
        self.driver.set_window_size(1024, 768)
        self.shipping_rate = 0.75  # $rate/lb
        self.outfile = "../data/toys_20160203.csv"
        self.fieldnames = ('net', 'roi', 'name', 'price', 'az_price', 'weight', 'az_sales_rank', 'az_match', 'url', 'img', 'az_url')
        self.url_cats = settings['toys']
        self.site_url = settings['site_url']
        self.page_url = settings['page_url']
        self.base_url = strip_final_slash(get_base_url(self.site_url))
        self.az = AZ()
        self.pc = 0

    def scrape(self, pc=None, change_url=None):
        """

        :param change_url is the changing part of wider site url, if there
        are multiple sections to hit.
        """
        self.run = True  # initialization of a site/section.
        if pc is not None:
            self.pc = pc
        while self.run is True:
            url = self.next_page_url(build_search_url(self.site_url, change_url, self.page_url))
            try:
                page = self.get_page(url)
            except Exception as e:
                print("Error with %s and skipped" % url)
                continue
            self.get_list(page)
        if change_url is None:
            print("Site %s finished" % self.site_url)
        else:
            print("Section %s finished" % change_url)
        self.driver.quit()

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
            return round(float(re.match(r'\$(\d+.\d\d)', f.strip()).group(1)), 2)
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
        return round(net, 2)

    def get_roi(self, data):
        net = self.get_dollar_amount(data['net'])
        price = self.get_dollar_amount(data['price'])
        return round(net/price, 2)

    def get_list(self, page):
        entries = page.find("ul", {"class": "tile-list-grid"})
        for e in entries:
            if len(e) == 1:
                continue
            elif e.name == "script":
                continue
            else:
                imitate_user(1)
                entry = {}
                try:
                    entry['name'] = e.find("a", {"class":"js-product-title"}).get_text().strip()
                except:
                    continue
                if 'http://' in e.find("a", {"class":"js-product-title"}).attrs['href']:
                    entry['url'] = e.find("a", {"class":"js-product-title"}).attrs['href']
                else:
                    entry['url'] = "".join((self.base_url, e.find("a", {"class":"js-product-title"}).attrs['href']))
                entry['price'] = e.find("span", {"class":"price-display"}).get_text()
                entry['img'] = e.find("img", {"class":"product-image"}).attrs['data-default-image']
                entry['az_price'], entry['weight'], entry['az_sales_rank'], entry['az_match'], entry['az_url'] = self.az.find_best_match(entry['name'], 'Toys')
                entry['net'] = self.get_net(entry)
                entry['roi'] = self.get_roi(entry)
                self.process_output(entry)

    def next_page_url(self, url):
        self.pc += 1
        imitate_user(1)
        next_url = url
        if self.page_url:
            next_url += self.page_url
        next_url += str(self.pc)
        if self.pc == 1:
            self.run = False  # recursion limit
        return next_url

    def get_page(self, url):
        try:
            print("Getting %s" % url)
            self.driver.get(url)
            # self.driver.get_cookies()
        except ValueError as e:
            imitate_user(5)
            try:
                self.driver.get(url)
            except:
                raise
        except Exception as e:
            print(url, e)
        # try:
        #     wait = WebDriverWait(self.driver, 3)
        #     wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div")))
        # except Exception as e:
        #     print("WebDriverWait error")
        page = BeautifulSoup(self.driver.page_source, "lxml")
        return page


if __name__ == '__main__':
    scraper = WalmartScraper()
    scraper.init_output()
    for cat in scraper.url_cats:
        scraper.scrape(0, cat)
