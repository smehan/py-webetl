import json
import csv
import os
import yaml
import pprint
from Gmap import map_api as goog

def get_all_coords():
    data = {}
    with open("../data/input/n-2.txt") as infh:
        for line in infh:
            parts = line.split("\t")
            c = (parts[9], parts[10].strip())
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


def output_data(data, path, json=False):
    names = ('name', 'address', 'zip', 'plid', 'id')
    if json is True:
        with open(path, 'w') as fh:
            json.dump(data, fh)
    elif not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as fh:
            outwriter = csv.DictWriter(fh, fieldnames=names, delimiter='\t')
            outwriter.writeheader()
    else:
        with open(path, 'a') as fh:
            outwriter = csv.DictWriter(fh, names, delimiter='\t')
            outwriter.writerows(data)


if __name__ == '__main__':
    path = "../data/output/sample-search.json"
    extract = goog.Gmap()  # build a gmap object to handle interface with google maps api.
    coord_dict = get_all_coords()
    places = {}
    for k in coord_dict:
        result = []
        coords = coord_dict[k]
        result = extract.fetch_results(coords, rad=5000)
        places = add_places(result, places, k)
    # pprint.pprint(places)
    output_data(places, path)
    print("********************Job Finished************************************")