"""
https://www.google.com/maps/search/laundromats+in+ALBERTSON,+NY/@40.7192859,-73.749286,13z/data=!3m1!4b1
"""

import yaml
import json
import time
from gmaps import Geocoding, client
from urllib.request import Request
from urllib.request import urlopen
import pprint


class Gmap():
    """"""

    def __init__(self,):
        """Constructor for Gmap"""
        with open("google_config.yaml", 'r') as f:
            settings = yaml.load(f)
        self.api_key = settings['GOOGLE_API_KEY']

    def oidhirp(self):
        resultsList = []
        count = 0
        lat = 40.7236
        long = -73.7058
        radius = 5000
        url = self._build_url(lat, long, radius=radius)
        req = Request(url)
        r = json.loads(urlopen(req).read().decode('utf-8'))
        for place in r['results']:
            resultsList.append(place)
            count += 1
        if r['next_page_token']:
            time.sleep(2)
            while True:
                npt = r['next_page_token']
                url = self._build_url(lat, long, radius=radius, npt=npt)
                req = Request(url)
                r = json.loads(urlopen(req).read().decode('utf-8'))

                for place in r['results']:
                    resultsList.append(place)
                    count += 1

                try:
                    r['next_page_token']
                except:
                    break
        pprint.pprint(resultsList)
        with open("../data/output/sample-search.json", 'w') as outf:
            json.dump(resultsList,outf)
        pprint.pprint(r)
        print(count)

    def _search_google(self):
        1+1

    def _build_url(self, lat, long, radius=5000, npt=None):
        """
        Builds up REST API query for Google Maps API nearby places search
        :param lat:
        :param long:
        :param radius:
        :param npt:
        :return:
        """
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='
        url += str(lat)
        url += ','
        url += str(long)
        url += '&radius='
        url += str(radius)
        url += '&types=laundry'
        url += '&key='
        url += self.api_key
        if npt is not None:
            url += '&pagetoken='
            url += str(npt)
        return url




if __name__ == '__main__':
    extract = Gmap()
    extract.oidhirp()