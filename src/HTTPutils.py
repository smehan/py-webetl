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
import time
import http  # this seems to be needed for exception handling in http client
from config import settings  # local config file


def define_headers(header_type):
    if header_type == 1:
        return({"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language":"en-US,en;q=0.8",
                "Cookie":"FUID=1277301928; D_SID=66.214.195.230:9Oud/j/NKc695t+b15WXsOzXkfTDziv+jv7o46J8dE4; superCookie=cachedVersion%3Dtemplates-1.2.75%26cachedChannel%3Dyellbeta%26cachedFiles%3Dstyles%252Fcore.css%257Cmodules%252FPage%252Fhome%252Fstyles%252Fmain.css%257Ccore.js%257Cmodules%252FPage%252Fserp%252Fstyles%252Fmain.css%257Cmodules%252FPage%252Fbip%252Fstyles%252Fmain.css%26CookiePolicy%3D1; JSESSIONID=7C1D4B406B4A1D6ABD1CD3502039243E; s_sq=%5B%5BB%5D%5D; useMultimap=OFF; SearchHistory0=14535107512433426; ScraperTracking=7kTnT68TSJdY9ScuQKm3; SearchedSession=true; AUTOKW2=0pizza; AUTOLOC=united+kingdom; s_fid=63DA4D9E9DDBDAF2-3E880F8E669AABC6; s_cc=true; s_vi=[CS]v1|2B4F960685011479-600001316005B11F[CE]; SEARCH_LOC=United%20Kingdom-%3A-United%20Kingdom-%3A-%0A53.59622935-%3A--1.75987285%0A-%3A-%0ACountry%0A-%3A-UNITED%20KINGDOM; SEARCH_KEYWORDS=pizza; _ga=GA1.2.98864706.1453272078; RT=sl=4&ss=1453338560468&tt=76693&obo=0&sh=1453511170570%3D4%3A0%3A76693%2C1453510759897%3D3%3A0%3A50911%2C1453510013661%3D2%3A0%3A39028%2C1453508704658%3D1%3A0%3A14251&dm=yell.com&si=6b0fdd38-eb27-4087-a84e-97bf70676799&bcn=%2F%2F36f1f369.mpstat.us%2F&r=https%3A%2F%2Fwww.yell.com%2Fucs%2FUcsSearchAction.do%3F24005052db7a2c87c5d9de43dd418adb&ul=1453512809733&hd=1453512810364; D_PID=C2974EEC-C295-3B19-881B-3987D348B229; D_IID=2E8928B6-5A9A-3071-AB7B-67971A1A0D51; D_UID=39BAF301-FC9A-3D89-8A8C-24C73B90F925; D_HID=2+MzGliJiPfl395tghgZQXqG5SLvXkhHMUcARWuinRQ; NSC_mcw_xxx-b.zfmmhspvq.dpn_80=ffffffffc3a0421f45525d5f4f58455e445a4a421517"})
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


def immitate_user():
    random.seed()
    delay = random.random()*60
    time.sleep(delay)


def init_tor(header_type):
    try:
        rotate_ip()
        immitate_user()
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