# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
from config import settings  # local config file
from HTTPutils import *


def get_details(entry):
    this_page, base_url = get_page(entry['url'], 1)
    try:
        entries = this_page.find("div", {"id": "inspection-reports-main"}).find_all("p")
        entry['URN'] = entries[0].find("strong").get_text()
        entry['street'] = entries[1].contents[0]
        entry['town'] = entries[1].contents[2]
        entry['parish'] = entries[1].contents[4]
        entry['postalcode'] = entries[1].contents[6]
        entry['Phone'] = entries[2].contents[0]
    except Exception as e:
        print("Failed to get details for %s" % entry['url'])
    return(entry)


def get_list(page, data, base_url):
    entries = page.find("ul", {"class": "resultsList"}).find_all("li")
    for e in entries:
        entry = {}
        entry['name'] = e.find("a").get_text()
        entry['url'] = ("".join((strip_final_slash(base_url),e.find("a").attrs['href'])))
        entry['address'] = e.find("p").get_text()
        entry['URN'] = e.find("p").find_next_sibling("p").get_text()
        entry['Provider'] = e.find("p").find_next_sibling("p").find_next_sibling("p").get_text()
        entry = get_details(entry)
        data[entry['name']] = entry
    return(data)


def process_page(page, base_url, current_url, output, pc, recursion_limit):
    output = get_list(page, output, base_url)
    pc += 1  # page count up 1
    if pc <= recursion_limit:
        next_url = "".join(("http://reports.ofsted.gov.uk/inspection-reports/find-inspection-report/results/1/any/any/any/any/any/any/rg42%201ya/20/any/0/0?page=",str(pc)))
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
    initial_url = "http://www.medspa.com/united-states?page=1&&reviews&sort=name%20ASC"
    initial_url = "http://reports.ofsted.gov.uk/inspection-reports/find-inspection-report/results/1/any/any/any/any/any/any/rg42%201ya/20/any/0/0?page=0"
    output = {}
    page, base_url = get_page(initial_url, 1)
    data = process_page(page, base_url, initial_url, output, 1, 2)
    process_output(data)
    print("Job finished. ***************************************")


if __name__ == '__main__':
    main()



