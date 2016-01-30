# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
#  -*- coding: utf-8 -*-

import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from amazon.api import AmazonAPI, AmazonSearch
from HTTPutils import get_base_url, strip_final_slash, immitate_user
import csv
import os
import time


dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
)

initial_url = "http://www.walmart.com/browse/toys/action-figures/4171_4172/?page="
# initial_url = 'http://www.dailybusinessreview.com/miami-dade-county?slreturn=20160028194706&atex-class=123&start=11&end=20'


test_xml = '<?xml version="1.0" ?><ItemLookupResponse xmlns="http://webservices.amazon.com/AWSECommerceService/2013-08-01"><OperationRequest><HTTPHeaders><Header Name="UserAgent" Value="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"></Header></HTTPHeaders><RequestId>2386c578-2872-40fe-aab9-9846d157bb69</RequestId><Arguments><Argument Name="AWSAccessKeyId" Value="AKIAJ4CJCEX5VUXSOEPQ"></Argument><Argument Name="AssociateTag" Value="berryland-20"></Argument><Argument Name="IdType" Value="ISBN"></Argument><Argument Name="ItemId" Value="0136042597"></Argument><Argument Name="Operation" Value="ItemLookup"></Argument><Argument Name="ResponseGroup" Value="Reviews"></Argument><Argument Name="ReviewPage" Value="1"></Argument><Argument Name="SearchIndex" Value="Books"></Argument><Argument Name="Service" Value="AWSECommerceService"></Argument><Argument Name="Timestamp" Value="2016-01-28T23:45:24Z"></Argument><Argument Name="Version" Value="2013-08-01"></Argument><Argument Name="Signature" Value="CyY+3ZbUW9x9tobruojeMYdRngDBPZdI+kk3aUjU4Fs="></Argument></Arguments><RequestProcessingTime>0.0680730000000000</RequestProcessingTime></OperationRequest><Items><Request><IsValid>True</IsValid><ItemLookupRequest><IdType>ISBN</IdType><ItemId>0136042597</ItemId><ResponseGroup>Reviews</ResponseGroup><SearchIndex>Books</SearchIndex><VariationPage>All</VariationPage></ItemLookupRequest></Request><Item><ASIN>0136042597</ASIN><CustomerReviews><IFrameURL>http://www.amazon.com/reviews/iframe?akid=AKIAJ4CJCEX5VUXSOEPQ&amp;alinkCode=xm2&amp;asin=0136042597&amp;atag=berryland-20&amp;exp=2016-01-29T23%3A52%3A04Z&amp;v=2&amp;sig=mGtz6x7pNYoKnFFyq%2BkCYgpBIHYVWq2t%2B8Nhg6sz%2Fn8%3D</IFrameURL><HasReviews>true</HasReviews></CustomerReviews></Item><Item><ASIN>B008VIWTIY</ASIN><CustomerReviews><IFrameURL>http://www.amazon.com/reviews/iframe?akid=AKIAJ4CJCEX5VUXSOEPQ&amp;alinkCode=xm2&amp;asin=B008VIWTIY&amp;atag=berryland-20&amp;exp=2016-01-29T23%3A52%3A04Z&amp;v=2&amp;sig=zOUyC%2BDfG5b3tHc%2F3x4%2FFPYA4Y0UDV%2FWWyC2I6TmLjA%3D</IFrameURL><HasReviews>true</HasReviews></CustomerReviews></Item></Items></ItemLookupResponse>'

class WalmartScraper(object):
    def __init__(self):
        self.driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
        self.driver.set_window_size(1024, 768)
        self.base_url = strip_final_slash(get_base_url(initial_url))
        self.pc = 10
        self.shipping_rate = 0.75  # $rate/lb
        self.run = True
        self.outfile = "../data/action_figs_20160129.csv"
        self.fieldnames = ('net', 'roi', 'name', 'price', 'az_price', 'weight', 'url', 'img')

    def scrape(self):
        while self.run is True:
            url = self.next_page_url()
            try:
                page = self.get_page(url)
            except Exception as e:
                print("Error with %s and skipped" % url)
                continue
            self.get_list(page)
        print("Job Finished!")
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

    def get_shipping_weight(self, entry):
        try:
            sp = self.get_page(entry['url'])
        except Exception as e:
            print("%s raised %s" % (entry['url'], e))
            immitate_user()
            return "Weight not fetched"  # TODO: consider an error list
        try:
            weight = sp.find("td", text=re.compile(r'Shipping')).next_sibling.next_sibling.get_text()
        except Exception as e:
            weight = "Not Available"
        return(weight)

    def get_dollar_amount(self, f):
        if isinstance(f, str):
            return round(float(f.replace('$','')), 2)
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
        net = (az_price - (price*1.08 + az_price*0.3 + weight*self.shipping_rate))
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
                entry = {}
                entry['name'] = e.find("a", {"class":"js-product-title"}).get_text().strip()
                if 'http://' in e.find("a", {"class":"js-product-title"}).attrs['href']:
                    entry['url'] = e.find("a", {"class":"js-product-title"}).attrs['href']
                else:
                    entry['url'] = "".join((self.base_url, e.find("a", {"class":"js-product-title"}).attrs['href']))
                entry['price'] = e.find("span", {"class":"price-display"}).get_text()
                entry['img'] = e.find("img", {"class":"product-image"}).attrs['data-default-image']
                entry['weight'] = self.get_shipping_weight(entry)
                entry['az_price'] = self.get_az_price(entry['name'])
                entry['net'] = self.get_net(entry)
                entry['roi'] = self.get_roi(entry)
                self.process_output(entry)

    def next_page_url(self):
        self.pc += 1
        immitate_user()
        next = initial_url
        next += str(self.pc)
        if self.pc == 3:
            self.run = False  # recurssion limit
        return next

    def get_page(self, url=None):
        if url is None:
            url = initial_url
        try:
            print("Getting %s" % url)
            self.driver.get(url)
            # self.driver.get_cookies()
        except ValueError as e:
            time.sleep(5)
            try:
                self.driver.get(url)
            except:
                raise
        except Exception as e:
            print(url, e)
        try:
            wait = WebDriverWait(self.driver, 3)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div")))
        except Exception as e:
            print("WebDriverWait error")
        page = BeautifulSoup(self.driver.page_source, "lxml")
        return page

    def get_az_price(self, title):  #TODO: going to need a dict of categories to insert into url
        amazon = AmazonAPI('***','berryland-20')
        az_price = 1000000.0
        try:
            products = amazon.search(Title=title, SearchIndex='Toys')
            for i, p in enumerate(products):
                price = p.price_and_currency[0]
                if price < az_price:
                    az_price = price
        except Exception as e:  #  amazon.api.SearchException doesn't work as doesn't inherit from BaseException
            if az_price == 1000000.0:
                az_price = 0.0
        return az_price


if __name__ == '__main__':
    scraper = WalmartScraper()
    scraper.init_output()
    scraper.scrape()
