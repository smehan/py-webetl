# -*- coding: UTF-8 -*-
from Pydb import *
import os
import csv


class Populate():
    """"""

    def __init__(self,):
        """Constructor for Populate"""
        self.acsdb = Mysql("../Pydb/mysql_config.yaml")

    def load_census_2010_zip_to_tracts(self):
        zips = []
        tract = []  # "ID","state","zipcode","census_tract_id","census_tract_name"
        with open("data/census_2010_zipcodes_to_tracts.csv") as fh:
            reader = csv.reader(fh)
            index = 0
            for r in reader:
                if index == 0:  # skip header
                    index += 1
                    continue
                zips.append([r[2], r[1]])  # zip, state
                tract.append([r[3], r[4], r[2]])  # id, name, zip
                index += 1
        with self.acsdb.con.cursor() as cursor:
            for z in zips:
                sql = "INSERT INTO `zip` (`zipcode`, `state`) VALUES (%s, %s)"
                cursor.execute(sql, (z[0], z[1]))
            self.acsdb.con.commit()
            for t in tract:
                zip_id_sql = "SELECT `pk_id` FROM `zip` WHERE `zipcode`=%s"
                cursor.execute(zip_id_sql, (t[2],))
                zip_id = cursor.fetchone()
                sql = "INSERT INTO `census_tract_2010` (`track_id`,`track_name`,`zip_id`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (t[0], t[1], zip_id['pk_id']))
            self.acsdb.con.commit()

    def load_geo_details(self):
        geo = {}
        with open("data/US/US.txt") as fh:
            reader = csv.reader(fh, delimiter='\t')
            for r in reader:
                geo[r[1]] = [{'city': r[2]}, {'county': r[5]}, {'lat': r[9]}, {'lon': r[10]}]
        with self.acsdb.con.cursor() as cursor:
            for g in geo:
                get_zip_id_sql = "SELECT `pk_id` FROM `zip` WHERE `zipcode`=%s"
                cursor.execute(get_zip_id_sql, (g))
                zip_id = cursor.fetchone()
                update_sql = "UPDATE `zip` SET `city`=%s, `county`=%s, `lat`=%s, `lon`=%s WHERE `zipcode`=%s"
                try:
                    cursor.execute(update_sql, (geo[g][0]['city'], geo[g][1]['county'], geo[g][2]['lat'], geo[g][3]['lon'], g))
                except:
                    pass
                self.acsdb.con.commit()


if __name__ == '__main__':
    pop = Populate()
    pop.load_census_2010_zip_to_tracts()
    pop.load_geo_details()


