import json
import csv
import yaml
import pprint
from Gmap import map_api as goog

def get_all_coords():
    data = {}
    with open("../data/input/nassau.txt") as infh:
        for line in infh:
            parts = line.split("\t")
            c = (parts[9],parts[10].strip())
            data[parts[1]] = c
        return(data)

def add_places(g, d, zip):
    for e in g:
        if e['name'] in d:
            continue
        else:
            details = [{'address': e['vicinity']}, {'zip': zip}, {'plid': e['place_id']}, {'id': e['id']}]
            d[e['name']] = details
    return d


def clean_places(places):
    for p in places:
        1+1



if __name__ == '__main__':
    extract = goog.Gmap()  # build a gmap object to handle interface with google maps api.
    coord_dict = get_all_coords()
    places = {}
    for k in coord_dict:
        result = []
        coords = coord_dict[k]
        result = extract.fetch_results(coords, rad=5000)
        places = add_places(result, places, k)
    # pprint.pprint(places)
    with open("../data/output/sample-search.json", 'w') as outf:
        json.dump(places, outf)
    print("********************Job Finished************************************")