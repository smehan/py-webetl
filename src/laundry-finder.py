import json
import csv
import yaml
import pprint
from Gmap import map_api as goog


if __name__ == '__main__':
    extract = goog.Gmap()
    lat = 40.7236
    long = -73.7058
    coords = (lat, long)
    resultsList = extract.fetch_results(coords, rad=5000)
    pprint.pprint(resultsList)
    with open("../data/output/sample-search-2.json", 'w') as outf:
        json.dump(resultsList, outf)