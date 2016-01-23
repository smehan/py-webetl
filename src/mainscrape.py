# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
from config import settings  # local config file
from HTTPutils import *


def get_details(entry):
    this_page, base_url = get_page(entry['url'], 1)
    try:
        entries = this_page.find("strong", {"itemprop": "telephone"}).get_text()
        # entry['URN'] = entries[0].find("strong").get_text()
        # entry['street'] = entries[1].contents[0]
        # entry['town'] = entries[1].contents[2]
        # entry['parish'] = entries[1].contents[4]
        # entry['postalcode'] = entries[1].contents[6]
        entry['Phone'] = entries
    except Exception as e:
        print("Failed to get details for %s" % entry['url'])
    return(entry)


# page.find("div", {"class":"col-sm-24 businessCapsule businessCapsule-fle js-LocalBusiness"})
def get_list(page, data, base_url):
    entries = page.find_all("div", {"class": "businessCapsule"})
    for e in entries:
        entry = {}
        entry['name'] = e.find("div", {"class":"businessCapsule--title"}).h2.get_text()
        entry['url'] = "".join((strip_final_slash(base_url),e.find("div", {"class":"businessCapsule--title"}).a.attrs['href']))
        # entry['address'] = e.find("p").get_text()
        # entry['URN'] = e.find("p").find_next_sibling("p").get_text()
        # entry['Provider'] = e.find("p").find_next_sibling("p").find_next_sibling("p").get_text()
        entry = get_details(entry)
        data[entry['name']] = entry
    return(data)


def process_page(page, base_url, current_url, output, pc, recursion_limit):
    output = get_list(page, output, base_url)
    pc += 1  # page count up 1
    if pc <= recursion_limit:
        next_url = "".join(("https://www.yell.com/ucs/UcsSearchAction.do?keywords=pizza&location=United+Kingdom&pageNum=",str(pc)))
        page, base_url = get_page(next_url, 1)
        output = process_page(page, base_url, next_url, output, pc, recursion_limit)
    return(output)


def process_output(data):
    index = 0  # count of data elements
    if data is None:
        print("There is no data to output")
    else:
        for r in data:
            print("Row ", index, ": ", r," : ", data[r])
            index += 1


def main():
    initial_url = "http://mugshots.louisvilleky.gov/archonixxjailsiteslmdc/archonixxjailpublic/"
    initial_url = "https://www.yell.com/ucs/UcsSearchAction.do?keywords=pizza&location=United+Kingdom&pageNum=8"
    # TODO need to clean this up so that I can pass the initial_cookie and initial_url as part of the object init
    output = {}
    page, base_url = get_page(initial_url, 1)
    data = process_page(page, base_url, initial_url, output, 1, 2)
    process_output(data)
    print("Job finished. ***************************************")


if __name__ == '__main__':
    main()



