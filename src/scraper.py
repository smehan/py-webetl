import re

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from HTTPutils import get_base_url, strip_final_slash


dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) Chrome/15.0.87"
)

initial_url = 'https://l3com.taleo.net/careersection/l3_ext_us/jobsearch.ftl'
# initial_url = 'http://www.google.com'
initial_url = "http://www.walmart.com/browse/toys/action-figures/4171_4172/?page=6"

class WalmartScraper(object):
    def __init__(self):
        self.driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
        self.driver.set_window_size(1024, 768)
        self.base_url = strip_final_slash(get_base_url(initial_url))

    def scrape(self):
        page = self.get_page()
        self.get_list(page)
        print("Job Finished!")
        self.driver.quit()

    def process_output(self, data):
        print("Item: %s | Price: %s | Weight: %s | URL: %s | img_url: %s" % (data['name'],data['price'],data['weight'],data['url'],data['img']))

    def get_shipping_weight(self, entry):
        url = "".join((self.base_url, entry['url']))
        sp = self.get_page(url)
        try:
            weight = sp.find("td", text=re.compile(r'Shipping')).next_sibling.next_sibling.get_text()
        except Exception as e:
            weight = "Not Available"
        return(weight)

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
                entry['url'] = e.find("a", {"class":"js-product-title"}).attrs['href']
                entry['price'] = e.find("span", {"class":"price-display"}).get_text()
                entry['img'] = e.find("img", {"class":"product-image"}).attrs['data-default-image']
                entry['weight'] = self.get_shipping_weight(entry)
                self.process_output(entry)


    def get_page(self, url=None):
        if url is None:
            url = initial_url
        self.driver.get(url)
        self.driver.get_cookies()
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div")))
        except Exception as e:
            print(e)
        page = BeautifulSoup(self.driver.page_source, "lxml")
        return(page)

if __name__ == '__main__':
    scraper = WalmartScraper()
    scraper.scrape()
