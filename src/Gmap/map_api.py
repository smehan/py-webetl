"""
Class that will make a search for nearby places of a particular type given a lat, long
"""

import yaml
import json
import time
from gmaps import Geocoding, client
from urllib.request import Request
from urllib.request import urlopen


class Gmap():
    """"""

    def __init__(self,):
        """Constructor for Gmap"""
        with open("Gmap/google_config.yaml", 'r') as f:  #  TODO: needs to look in same dir
            settings = yaml.load(f)
        self.api_key = settings['GOOGLE_API_KEY']

    def fetch_results(self, coords, rad=1000):
        """
        Takes a coordinate tuple and a radius and fetches a result set.
        Predetermined url at this point.
        :param coords: a tuple of lat and long for this search
        :param rad: radius of search
        :return: list of json results
        """
        resultsList = []
        r = self._search_google(coords[0], coords[1], rad)
        if r['status'] == 'OVER_QUERY_LIMIT':
            print("Google quota exceeded. Cool down!")
            return []
        for place in r['results']:
            resultsList.append(place)
        if 'next_page_token' in r:
            time.sleep(2)
            while True:
                npt = r['next_page_token']
                r = self._search_google(coords[0], coords[1], rad, npt)
                for place in r['results']:
                    resultsList.append(place)
                try:
                    r['next_page_token']
                except:
                    break
        print("Google maps searched and results returned for %s, %s." % (coords[0], coords[1]))
        return resultsList

    def _search_google(self, lat, long, r, npt=None):
        url = self._build_url(lat, long, radius=r, npt=npt)
        req = Request(url)
        r = json.loads(urlopen(req).read().decode('utf-8'))
        return r

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
        url += '&keyword=laundromat'  # keyword: "(cinema) OR (theater)" unclear if it works
        url += '&key='
        url += self.api_key
        if npt is not None:
            url += '&pagetoken='
            url += str(npt)
        return url




if __name__ == '__main__':
    extract = Gmap()
    r = extract.fetch_results()