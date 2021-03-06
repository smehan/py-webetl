# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
#  -*- coding: utf-8 -*-

# standard libs
import re
import os
import time
import datetime
import logging
import csv
import itertools
import pickle
# 3rd party
import yaml
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
# application libs
from HTTPutils import get_base_url, strip_final_slash, imitate_user, build_search_url
from loggerUtils import init_logging



dcap = dict(DesiredCapabilities.PHANTOMJS)  # TODO: split this out into config
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
)


class WikiScraper(object):
    def __init__(self):
        init_logging(default_path='../loggerUtils/logging.yml')
        self.logger = logging.getLogger(__name__)
        self.logger.info("Wiki Geo object initialized and logging enabled")

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"wiki_config.yml"), "r") as fh:
            settings = yaml.load(fh)

        self.driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
        self.driver.set_window_size(1024, 768)
        self.outfile = settings['output']
        self.depth_limit = settings['depth_limit']
        self.debug = settings['debug']
        self.reuse = settings['reuse']
        self.fieldnames = ('FIPS', 'GNIS', 'area-codes', 'county', 'county-url', 'density-2010-sqkm',
                           'density-2010-sqmi', 'elevation-ft', 'elevation-m', 'geohack-url',
                           'land-area', 'lat', 'location-img', 'census-map',
                           'long', 'place-name', 'place-type', 'place-url',
                           'place-www', 'pop-2010', 'pop-estimate', 'state',
                           'state-url', 'total-area', 'water-area', 'zips')
        self.top_url = settings['top_url']
        self.base_url = strip_final_slash(get_base_url(self.top_url))

    def destroy(self):
        """
        method to destroy all objects and clean up.
        :return:
        """
        self.logger.info("Wiki object cleanly destroyed...")
        self.driver.quit()

    def start_scrape(self):
        """
        Fetches top url, builds up recursively the leaves of each level of the hierarchy, adding
        that additional level each trip, until it has the leaves. Then passes all the leaves to the
        harvester to extract the content.
        :return:
        """
        self.run = True  # initialize run
        topcats = self._build_cats(self.get_page(self.top_url), lvl='us')
        if self.reuse and os.path.exists('../../data/statecats.pickle'):
            with open('../../data/statecats.pickle', 'rb') as fh:
                statecats = pickle.load(fh)
            self.logger.info("States taken from a previous run...")
        else:
            statecats = list(itertools.chain.from_iterable([self._build_cats(self.get_page(c[1]), lvl='type') for c in topcats]))
            with open('../../data/statecats.pickle', 'wb') as fh:
               pickle.dump(statecats, fh, pickle.HIGHEST_PROTOCOL)
        if self.reuse and os.path.exists('../../data/countycats.pickle'):
            with open('../../data/countycats.pickle', 'rb') as fh:
                countycats = pickle.load(fh)
            self.logger.info("Counties taken from a previous run...")
        else:
            countycats = list(itertools.chain.from_iterable([self._build_cats(self.get_page(s[2]), lvl='state') for s in statecats]))
            with open('../../data/countycats.pickle', 'wb') as fh:
               pickle.dump(countycats, fh, pickle.HIGHEST_PROTOCOL)
            self.logger.info("Leaves taken from a previous run...")
        if self.reuse and os.path.exists('../../data/leaves.pickle'):
            with open('../../data/leaves.pickle', 'rb') as fh:
                leaves = pickle.load(fh)
            self.logger.info("Leaves taken from a previous run...")
        else:
            leaves = list(itertools.chain.from_iterable([self._build_cats(self.get_page(c[3]), lvl='county') for c in countycats]))
            with open('../../data/leaves.pickle', 'wb') as fh:
               pickle.dump(leaves, fh, pickle.HIGHEST_PROTOCOL)
        leaf_index = 0
        for leaf in leaves:
            self._progress(leaf_index, len(leaves))
            if leaf[1] is None:
                continue
            try:
                self._extract_leaf(self.get_page(leaf[4]), url=leaf[4])
            except Exception as e:
                self.logger.warn("Problem with {} and skipped ....".format(leaf[4]))
            leaf_index += 1

    def _build_cats(self, page, lvl=None):
        """parse all the top level links and build a dictionary of containers to walk
        :param page: page is a bs4 object to parse
        :param lvl: string indicating what level of category container we are at.
        :return: a dict
        """
        # no level passed, error.
        if lvl is None:
            self.run = False
            return
        # no page found, return.
        if page.find("div", {"class": "noarticletext"}):
            self.run = False
            return
        # top level of US, lists place type containers
        elif lvl == 'us':
            block = page.find("div", {"class": "mw-category-group"})  # first block in the container page, which is US
            links = [(e.contents[0].split(" ")[0], "".join((self.base_url, e.attrs['href']))) for e in block.find_all("a", {"class": "CategoryTreeLabel"})]
            return links
        # place type level of US, lists all states with that place type
        elif lvl == 'type':  # TODO: need to replace this strcuture with a yield to remove intermediate list
            links = []
            block = page.find_all("div", {"class": "CategoryTreeItem"})
            for e in block:
                type, state = self._parse_link_title(e.a.contents[0], 'state')
                links.append((type, state, "".join((self.base_url, e.a.attrs['href']))))
            return links
        # state level of US, lists all counties with that place type
        elif lvl == 'state':
            links = []
            block = page.find_all("div", {"class": "CategoryTreeItem"})
            for e in block:
                type, county, state = self._parse_link_title(e.a.contents[0], 'county')
                links.append((type, county, state, "".join((self.base_url, e.a.attrs['href']))))
            return links
        # county level of US, lists all counties of a state with that place type
        elif lvl == 'county':
            links = []
            try:
                other_info = re.search(r'"(.*)"', page.find("div", {"id": "mw-pages"}).h2.contents[1]).group(1)
            except:
                try:
                    other_info = re.search(r':(.*)$', page.find("h1", {"id": "firstHeading"}).contents[0]).group(1)
                except:
                    other_info = None
            type, county, state = self._parse_link_title(other_info, 'county')
            block = page.find_all("a", string=re.compile(r'^[\w ]+, [\w ]+$'))
            for e in block:
                if ' in ' in e.contents[0]:  # to skip the /wiki/Category link in the page
                    continue
                place = self._parse_link_title(e.contents[0], 'place')
                links.append((type, place, county, state, "".join((self.base_url, e.attrs['href']))))
            return links

    def _parse_link_title(self, text, level):
        """
        computes 1,2,3 components based on level.
        If search failed to find target text, return filler strings.
        :param text: link text
        :return: components of type, (county), state
        """
        if text is None:
            return 'NA', 'NA', 'NA'
        if level == 'state':
            return self._get_place_type(text), self._get_state(text)
        elif level == 'county':
            return self._get_place_type(text), self._get_county(text), self._get_state(text)
        elif level == 'place':
            return self._get_place(text)

    @staticmethod
    def _get_place_type(text):
        """
        parse a string to determine which place type it contains
        :param text: string to parse
        :return:  a place type, e.g. City
        """
        types = [('VILLAGE', 'VILLAGES'), ('UNINC', 'UNINCORPORATED'), ('TOWN', 'TOWNS'),
                 ('HAMLET', 'HAMLETS'), ('CITY', 'CITIES'), ('BORO', 'BOROUGH'),
                 ('HISTORIC', 'FORMER'), ('CDP', 'CENSUS')]
        for t in types:
            if t[1] in text.upper().split(" ")[0]:
                return t[0]
        return None

    @staticmethod
    def _get_state(text):
        """ parse a string to determine which state it contains
        :param text: string to parse
        :return: a state abbreviation or None
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

    @staticmethod
    def _get_county(text):
        """ parse a string to extract which county it contains
        :param text: string to parse
        :return: a county string or None
        """
        try:
            county = re.search(r'in ([\w ]+) County,', text).group(1)
            return county.upper()
        except:
            return None

    @staticmethod
    def _get_place(text):
        """ parse a string to extract the place name it contains
        :param text: string to parse form of 'Williamston, North Carolina'
        :return: a place name as string or None
        """
        try:
            place = re.search(r'([\w ]+),', text).group(1)
            return place.upper()
        except:
            return None

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

    def _extract_leaf(self, page, url=None):
        """
        method takes page from source and parses out items to save. Then sends entry to process_output.
        :param page: bs4 object returned from get_page
        :param url: string of URL of page
        :return:
        """
        # no page found, return.
        if page.find("div", {"class": "noarticletext"}):
            self.run = False
            return
        entry = {'place-url': url}  # TODO:  consider a default dict
        try:
            block = page.find("table", {"class": "geography"})
            entries = block.find_all("tr")
        except:
            self.logger.warn("No geography vcard found...skipping")
            return
        for e in entries:
            if e.find("span", {"class": "fn"}):
                entry['place-name'] = re.search(r'([\w ]+),?', e.th.span.get_text()).group(1)
                continue
            if e.find("span", {"class": "category"}):
                entry['place-type'] = e.get_text().strip()
                continue
            if e.find(string='County'):
                entry['county'] = re.search(r'County\n([\w ]+)', e.get_text()).group(1)
                entry['county-url'] = "".join((self.base_url, e.td.a.get('href', 'None')))
                continue
            if e.find(string='State'):
                entry['state'] = self._get_state(re.search(r'State\n ?([\w ]*)', e.get_text()).group(1))
                entry['state-url'] = "".join((self.base_url, e.td.a.get('href', 'None')))
                continue
            if re.search(r'map', e.get_text(), re.I):
                if re.search(r'census', e.get_text(), re.I):
                    entry['census-map'] = "".join((self.base_url, e.a.get('href', 'None')))
                else:
                    entry['location-img'] = "".join((self.base_url, e.a.get('href', 'None')))
                continue
            if re.search(r'Coordinates:', e.get_text()):
                entry['geohack-url'] = "".join((self.base_url, e.a.get('href', 'None')))
                continue
            if e.find("span", {"class": "geo"}):
                entry['lat'], entry['long'] = re.search('\d+\.\d+; -?\d+\.\d+$', e.span.get_text()).group(0).split('; ')
                continue
            if re.search('Area(?! \w+)', e.get_text()):
                if re.search(r'\n([\d.]+)', e.next_sibling.next_sibling.get_text()):
                    entry['total-area'] = re.search(r'\n([\d\.,]+)', e.next_sibling.next_sibling.get_text()).group(1)
                if re.search(r'Land\n([\d\.,]+)', e.next_sibling.next_sibling.next_sibling.next_sibling.get_text()):
                    entry['land-area'] = re.search(r'Land\n([\d\.,]+)', e.next_sibling.next_sibling.next_sibling.next_sibling.get_text()).group(1)
                if re.search(r'Water\n([\d\.,]+)', e.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.get_text()):
                    entry['water-area'] = re.search(r'Water\n([\d\.,]+)', e.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.get_text()).group(1)
                continue
            if e.find(string='Elevation'):
                entry['elevation-ft'] = re.search(r'\n(\d+)', e.get_text()).group(1)
                entry['elevation-m'] = re.search(r'\((\d+)', e.get_text()).group(1)
                continue
            if re.search(r'Population', e.get_text()):
                if re.search(r'\n([\d,]+)', e.next_sibling.next_sibling.get_text()):
                    entry['pop-2010'] = re.search(r'\n([\d,]+)', e.next_sibling.next_sibling.get_text()).group(1)
                elif re.search(r'\n([\d,]+)', e.get_text()):
                    entry['pop-2010'] = re.search(r'\n([\d,]+)', e.get_text()).group(1)
                if re.search(r'Estimate', e.next_sibling.next_sibling.next_sibling.next_sibling.get_text()):
                    entry['pop-estimate'] = re.search(r'\n([\d,]+)', e.next_sibling.next_sibling.next_sibling.next_sibling.get_text()).group(1)
                elif re.search(r'City\n([\d,]+)', e.next_sibling.next_sibling.next_sibling.next_sibling.get_text()):
                    entry['pop-estimate'] = re.search(r'\n([\d,]+)', e.next_sibling.next_sibling.next_sibling.next_sibling.get_text()).group(1)
                continue
            if re.search(r'Density\n', e.get_text()):
                entry['density-2010-sqmi'] = re.search(r'([\d.,]+) ?/ ?sq', e.get_text()).group(1)
                entry['density-2010-sqkm'] = re.search(r'([\d.,]+) ?/ ?km', e.get_text()).group(1)
                continue
            if re.search(r'ZIP', e.get_text()):
                entry['zips'] = re.search(r'(\d.*)\[?', e.get_text()).group(1)
                continue
            if re.search(r'Area code', e.get_text()):
                entry['area-codes'] = re.search(r'\d.*', e.get_text()).group(0)
                continue
            if re.search(r'FIPS', e.get_text()):
                entry['FIPS'] = re.search(r'[\d-]+', e.get_text()).group(0)
                continue
            if e.find(string='GNIS'):
                entry['GNIS'] = re.search(r'\d+', e.get_text()).group(0)
                continue
            # there are some pages that have another entire panel below
            # the place, e.g., for a park. Need to skip them.
            # Last good entry should be the website.
            if re.search('Website', e.get_text()):
                if e.a:
                    entry['place-www'] = e.a.get('href', url)
                else:
                    entry['place-www'] = 'None'
                break
        self.process_output(entry)

    def get_page(self, url):
        try:
            imitate_user(0.2)
            self.logger.info("Getting %s" % url)
            self.driver.get(url)
        except ValueError as e:
            imitate_user(2)
            try:
                self.driver.get(url)
            except:
                raise
        except Exception as e:
            self.logger.error(url, e)
        page = BeautifulSoup(self.driver.page_source, "lxml")
        return page

    def _progress(self, part, total):
        """
        Displays a progress bar to indicate current search progress.
        :param part: the portion searched
        :param total: the total to search
        :return:
        """
        self.logger.info('{}% complete.'.format(round((part/total)*100, 4)))

if __name__ == '__main__':
    scraper = WikiScraper()
    scraper.init_output()
    scraper.start_scrape()
    scraper.destroy()
