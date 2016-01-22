# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
import re
import socks
import socket
from stem import Signal
from stem.control import Controller
import random
import http  # this seems to be needed for exception handling in http client
from config import settings  # local config file


def define_headers(header_type):
    if header_type == 1:
        return({"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language":"en-US,en;q=0.8"})
    else:
        return({"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language":"en-US,en;q=0.8"})


def rotate_ip():
    random.seed()
    if random.random() <= 0.05:
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password=settings['TOR_PASSPHRASE'])
                controller.signal(Signal.NEWNYM)
                print("Tor ip reset!")
        except Exception as e:
            print("Failed to contact Tor controller")


def init_tor(header_type):
    try:
        rotate_ip()
        socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
        socket.socket = socks.socksocket
        r = Request('http://icanhazip.com', headers=define_headers(header_type))
        test = urlopen(r).read()
        print("Tor network accessed and using ip: %s" % test.rstrip())  # check ip
    except:
        print("There was an error using the TOR network on localhost:9050")


def get_page(in_url, header_type):
    try:
        init_tor(header_type)
        req = Request(in_url, data=None, headers=define_headers(header_type))
        html = urlopen(req)
    except HTTPError as e:
        print("URL: %s - HTTP error: %s " % (in_url, e))
    except URLError as e:
        print("URL: %s - Server is not reachable: %s" % (in_url, e))
    except http.client.HTTPException as e:
        print(e)
    else:
        print("Retrieved requested URL: %s" % in_url.rstrip())

    base_url = get_base_url(in_url)

    try:
        bsObj = BeautifulSoup(html, 'lxml')
    except AttributeError as e:
        print("Page was not found: %s" % e)
    else:
        if bsObj is None:
            print("Page has no data: %s" % e)
        else:
            return(bsObj, base_url)


def get_base_url(url):
    try:
        base_url = re.match(r'^(http[s]?:\/\/[\w\.]*/)', url).group(1)
    except Exception as e:
        print("Can't find base url for %s" % url)
        base_url = None
    return(base_url)


def strip_final_slash(url):
    output = re.match(r'(.*)/', url).group(1)
    return(output)