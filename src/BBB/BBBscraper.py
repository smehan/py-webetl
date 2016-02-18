# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
#  -*- coding: utf-8 -*-

import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from HTTPutils import get_base_url, strip_final_slash, imitate_user, build_search_url
import yaml
import csv
import os


dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
)

class BBBScraper(object):
    def __init__(self):

        with open("bbb_config.yaml", "r") as f:
            settings = yaml.load(f)

        self.driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
        self.driver.set_window_size(1024, 768)
        self.outfile = settings['output']
        self.fieldnames = ('name', 'url', 'address', 'city', 'state', 'zip', 'phone', 'type', 'email', 'contact')
        self.url_cats = ''
        self.site_url = settings['site_url']
        self.page_url = settings['page_url']
        self.change_urls = settings['change_url']
        self.base_url = strip_final_slash(get_base_url(self.site_url))
        self.pc = 0

    def destroy(self):
        """
        method to destroy all objects and clean up.
        :return:
        """
        self.driver.quit()

    def scrape(self, pc=None, change_url=None):
        """

        :param change_url is the changing part of wider site url, if there
        are multiple sections to hit.
        :param pc is an integer indicating where to start with a paginated url.
        It also acts as a recursion limit, when to move on from a section.
        """
        self.run = True  # initialization of a site/section.
        if pc is not None:
            self.pc = pc
        while self.run is True:
            url = self.next_page_url(build_search_url(self.site_url, change_url))
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
        self.pc = 0  # re-init pc to run next section

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
        if page.find_all("div", {"class": "nme"}):
            entries = page.find_all("div", {"class": "nme"})
        elif page.find_all("div", {"class":"rdetails"}):
            entries = page.find_all("div", {"class": "rdetails"})
        elif page.find_all("div", {"class": "info"}):
            entries = page.find_all("div", {"class": "info"})
        # entries = page.find_all("div", {"class":"listing"})
        for e in entries:
            if len(e) == 1:
                continue
            elif e.name == "script":
                continue
            else:
                imitate_user(1)
                entry = {}
                entry = self.get_detail(e.a.attrs['href'], entry)
                if entry:
                    self.process_output(entry)

    def get_detail(self, url, e):
        """
        First checks to see if the previously found list had absolute urls or relative urls.
        If relative, concatenate to an absolute url. Then, if there is no name
        to add to the entry, then there is something terribly wrong with the entry in general so
        exit out.
        :param url: url of details page, which is fetched in method.
        :param e: dictionary object that is populated and returned
        :return: modified dictionary populated with details from fetched page.
        """
        if 'http' in url:
            page = self.get_page(url)
        else:
            page = self.get_page("".join((self.base_url,url)))
        try:
            e['name'] = page.find("h1", {"class": "business-title"}).get_text().strip()
        except:
            return
        e['url'] = self._get_bbb_url(url)
        e['phone'] = self._get_phone(page)
        e['address'] = self._get_address(page)
        e['city'] = self._get_city(page)
        e['state'] = self._get_state(page)
        e['zip'] = self._get_zip(page)
        e['email'] = self._get_email(page)
        e['type'] = self._get_type(page)
        e['contact'] = self._get_contact(page)
        return e

    def _get_bbb_url(self, url):
        try:
            data = url
        except:
            data = 'NULL'
        return data

    def _get_phone(self, page):
        data = 'NULL'
        if page.find("span", {"class": "business-phone"}):
            try:
                data = page.find("span", {"class": "business-phone"}).get_text().strip()
            except:
                pass
        return data

    def _get_address(self, page):
        data = 'NULL'
        if page.find("span", {"itemprop": "streetAddress"}):
            try:
                data = page.find("span", {"itemprop": "streetAddress"}).get_text().strip()
            except:
                pass
        elif page.find("span", {"class": "business-address"}).span:
            try:
                data = page.find("span", {"class": "business-address"}).span.get_text().strip()
            except:
                pass
        return data

    def _get_city(self, page):
        data = 'NULL'
        if page.find("span", {"itemprop": "addressLocality"}):
            try:
                data = page.find("span", {"itemprop": "addressLocality"}).get_text().strip()
            except:
                pass
        elif page.find("span", {"class": "business-address"}).span.next_sibling.next_sibling:
            try:
                data = page.find("span", {"class": "business-address"}).span.next_sibling.next_sibling.get_text().strip()
            except:
                pass
        return data

    def _get_state(self, page):
        data = 'NULL'
        if page.find("span", {"itemprop": "addressRegion"}):
            try:
                data = page.find("span", {"itemprop": "addressRegion"}).get_text().strip()
            except:
                pass
        elif page.find("span", {"class": "business-address"}).span.next_sibling.next_sibling.next_sibling.next_sibling.get_text().strip():
            try:
                data = page.find("span", {"class": "business-address"}).span.next_sibling.next_sibling.next_sibling.next_sibling.get_text().strip()
            except:
                pass
        return data

    def _get_zip(self, page):
        data = 'NULL'
        if page.find("span", {"itemprop": "postalCode"}):
            try:
                data = page.find("span", {"itemprop": "postalCode"}).get_text().strip()
            except:
                pass
        elif page.find("span", {"class": "business-address"}).span.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.get_text().strip():
            try:
                data = page.find("span", {"class": "business-address"}).span.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.get_text().strip()
            except:
                pass
        return data

    def _get_email(self, page):
        data = 'NONE'
        if page.find("span", re.compile('email')):
            try:
                data = page.find("span", re.compile('email')).a.get_text()
            except:
                pass
        elif page.find_all("span"):
            for text in page.find_all("span"):
                try:
                    if '@' in text.a.get_text():
                        data = text.a.get_text()
                except:
                    pass
        return data

    def _get_type(self, page):
        data = 'NULL'
        if page.find_all("h5"):
            for text in page.find_all("h5"):
                try:
                    if 'Type of Entity' in text.get_text():
                        data = text.p.get_text()
                except:
                    pass
        return data

    def _get_contact(self, page):
        data = 'NULL'
        if page.find_all("span"):
            for text in page.find_all("span"):
                try:
                    if 'Principal' in text.get_text() or 'Manager' in text.get_text():
                        data = text.get_text()
                except:
                    pass
        return data

    def next_page_url(self, url):
        """
        method to build the next url to be fetched. Expects a pagination parameter in the url
        and builds it iteratively. pc is the control parameter.
        :param url:
        :return:
        """
        self.pc += 1
        imitate_user(1)
        next_url = url
        if self.page_url:
            next_url += self.page_url
        # next_url += str(self.pc)
        if self.pc == 1:  # this should be the last param
            self.run = False  # recursion control
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
        page = BeautifulSoup(self.driver.page_source, "lxml")
        return page


if __name__ == '__main__':
    scraper = BBBScraper()
    scraper.init_output()
    # scraper.scrape()
    for cat in scraper.change_urls:
        scraper.scrape(change_url=cat)
    scraper.destroy()
