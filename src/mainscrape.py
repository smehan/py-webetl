# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
import re
import socks
import socket
import http  # this seems to be needed for exception handling in http client


def define_headers(header_type):
    if header_type == 1:
        return({"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language":"en-US,en;q=0.8"})
    else:
        return({"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language":"en-US,en;q=0.8"})


def get_page(in_url, header_type):
    try:
        socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
        socket.socket = socks.socksocket
        req = Request(in_url, data=None, headers=define_headers(header_type))
        html = urlopen(req)
        r = Request('http://icanhazip.com', headers=define_headers(header_type))
        test = urlopen(r).read()
        print(test)  # check ip
    except HTTPError as e:
        print("URL: %s - HTTP error: %s " % (in_url, e))
    except URLError as e:
        print("URL: %s - Server is not reachable: %s" % (in_url, e))
    except http.client.HTTPException as e:
        print(e)
    else:
        print("Retrieved requested URL: %s" % in_url)

    try:
        base_url = re.match(r'^(http[s]?:\/\/[\w\.]*/)', in_url).group(1)
    except:
        print("Can't find base url for %s" % in_url)
        base_url = None

    try:
        bsObj = BeautifulSoup(html, 'lxml')
    except AttributeError as e:
        print("Page was not found: %s" % e)
    else:
        if bsObj is None:
            print("Page has no data: %s" % e)
        else:
            return(bsObj, base_url)


def get_yell(page, data):
    print(page.body)
    entries = page.find_all("div", {"class": "businessCapsule"})
    for e in entries:
        print(e)
        data['name'] = e.find("div", {"class": "businessCapsule--title"}).h2.get_text()
        data['tel'] = e.find("strong", {"class": "businessCapsule--tel"}).get_text()
        data['yell-url'] = e.find("div", {"class": "businessCapsule--title"}).a.attrs['href']
    return(data)


def process_page(page):
    output = {}
    output = get_yell(page, output)
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
    initial_url = "https://www.yell.com/ucs/UcsSearchAction.do?keywords=pizza&location=United+Kingdom&pageNum=7"
    page, base_url = get_page(initial_url, 1)
    data = process_page(page)
    process_output(data)
    print("Job finished. ***************************************")



if __name__ == '__main__':
    main()



