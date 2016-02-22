# -*- coding: UTF-8 -*-
from Pydb import *
import os
import csv
import re


class Populate():
    """Builds the census_2010_schema with various tables.

    loads: census_2010 zips and tract ids.
    loads: US geo details for all states, counties, cities with zip, lat/long.
    """

    def __init__(self,):
        """Constructor for Populate"""
        self.acsdb = Mysql("../Pydb/mysql_config.yaml")

    def load_tracts(self):
        tracts = {}  # {track_id : track_name}
        with open("data/TRACT_ZIP_122015.csv") as fh:
            r_count = 0
            reader = csv.reader(fh)
            for r in reader:
                r_count += 1
                if r_count < 2:
                    continue
                tracts[r[0]] = self.get_tract_name(r[0])
        with self.acsdb.con.cursor() as cursor:
            for t in tracts:
                update_sql = "INSERT INTO `census_tract_2010` (`track_id`, `track_name`) VALUES (%s, %s)"
                try:
                    cursor.execute(update_sql, (int(t), tracts[t]))
                except:
                    pass
                self.acsdb.con.commit()

    def get_tract_name(self, tract_id):
        """Pulls out the Census Tract Name from up to the last 6 digits in the track_id.
        This is not finished since it is taking 020100 and yielding 0201.00 and it should
        drop the initial 0 and for suffixes with no information it should drop 00.

        :param tract_id: this is the full tract id from the input file
        """
        base = re.search(r'\d+(\d{4})(\d\d)', tract_id)
        name = ".".join((base.group(1), base.group(2)))
        return name

   #TRACT,ZIP,RES_RATIO,BUS_RATIO,OTH_RATIO,TOT_RATIO
    def load_tract_zip_crosswalk(self):
        pass

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

    def load_S2503(self):
        data = {}
        with open("data/ACS_14_5YR_S2503.csv") as fh:
            reader = csv.reader(fh)
            r_count = 0
            for r in reader:
                r_count += 1
                if r_count < 3:
                    continue
                name = re.search(r'[\w .]+', r[2]).group(0)
                r = [e.replace('-', '0') for e in r]
                r = [e.replace('(X)', '0') for e in r]
                r = [e.replace('**', '0') for e in r]
                data[name] = [{'HC01_VC01': float(r[3])},
                              {'HC02_VC01': float(r[4])},
                              {'HC03_VC01': float(r[5])},
                              {'HC01_VC03': float(r[9])},
                              {'HC02_VC03': float(r[10])},
                              {'HC03_VC03': float(r[11])},
                              {'HC01_VC04': float(r[12])},
                              {'HC02_VC04': float(r[13])},
                              {'HC03_VC04': float(r[14])},
                              {'HC01_VC05': float(r[15])},
                              {'HC02_VC05': float(r[16])},
                              {'HC03_VC05': float(r[17])},
                              {'HC01_VC06': float(r[18])},
                              {'HC02_VC06': float(r[19])},
                              {'HC03_VC06': float(r[20])},
                              {'HC01_VC07': float(r[21])},
                              {'HC02_VC07': float(r[22])},
                              {'HC03_VC07': float(r[23])},
                              {'HC01_VC08': float(r[24])},
                              {'HC02_VC08': float(r[25])},
                              {'HC03_VC08': float(r[26])},
                              {'HC01_VC09': float(r[27])},
                              {'HC02_VC09': float(r[28])},
                              {'HC03_VC09': float(r[29])},
                              {'HC01_VC10': float(r[30])},
                              {'HC02_VC10': float(r[31])},
                              {'HC03_VC10': float(r[32])},
                              {'HC01_VC11': float(r[33])},
                              {'HC02_VC11': float(r[34])},
                              {'HC03_VC11': float(r[35])},
                              {'HC01_VC12': float(r[36])},
                              {'HC02_VC12': float(r[37])},
                              {'HC03_VC12': float(r[38])},
                              {'HC01_VC13': float(r[39])},
                              {'HC02_VC13': float(r[40])},
                              {'HC03_VC13': float(r[41])},
                              {'HC01_VC14': float(r[42])},
                              {'HC02_VC14': float(r[43])},
                              {'HC03_VC14': float(r[44])}]
        with self.acsdb.con.cursor() as cursor:
            for r in data:
                get_track_id_sql = "SELECT `pk_id` FROM `census_tract_2010` AS c WHERE `track_name`=%s"
                cursor.execute(get_track_id_sql, (r))
                track_pk_id = cursor.fetchone()
                if track_pk_id is None:
                    continue
                update_sql = "UPDATE `census_tract_2010` SET `HC01_VC01`=%s," \
                             "`HC02_VC01`=%s," \
                             "`HC03_VC01`=%s," \
                             "`HC01_VC03`=%s," \
                             "`HC02_VC03`=%s," \
                             "`HC03_VC03`=%s," \
                             "`HC01_VC04`=%s," \
                             "`HC02_VC04`=%s," \
                             "`HC03_VC04`=%s," \
                             "`HC01_VC05`=%s," \
                             "`HC02_VC05`=%s," \
                             "`HC03_VC05`=%s," \
                             "`HC01_VC06`=%s," \
                             "`HC02_VC06`=%s," \
                             "`HC03_VC06`=%s," \
                             "`HC01_VC07`=%s," \
                             "`HC02_VC07`=%s," \
                             "`HC03_VC07`=%s," \
                             "`HC01_VC08`=%s," \
                             "`HC02_VC08`=%s," \
                             "`HC03_VC08`=%s," \
                             "`HC01_VC09`=%s," \
                             "`HC02_VC09`=%s," \
                             "`HC03_VC09`=%s," \
                             "`HC01_VC10`=%s," \
                             "`HC02_VC10`=%s," \
                             "`HC03_VC10`=%s," \
                             "`HC01_VC11`=%s," \
                             "`HC02_VC11`=%s," \
                             "`HC03_VC11`=%s," \
                             "`HC01_VC12`=%s," \
                             "`HC02_VC12`=%s," \
                             "`HC03_VC12`=%s," \
                             "`HC01_VC13`=%s," \
                             "`HC02_VC13`=%s," \
                             "`HC03_VC13`=%s," \
                             "`HC01_VC14`=%s," \
                             "`HC02_VC14`=%s," \
                             "`HC03_VC14`=%s" \
                             "WHERE `track_pk_id`=%s"
                try:
                    cursor.execute(update_sql, (data[r][0]['HC01_VC01'], data[r][1]['HC02_VC01'], data[r][2]['HC03_VC01'],
                                                data[r][0]['HC01_VC03'], data[r][1]['HC02_VC03'], data[r][2]['HC03_VC03'],
                                                data[r][0]['HC01_VC04'], data[r][1]['HC02_VC04'], data[r][2]['HC03_VC04'],
                                                data[r][0]['HC01_VC05'], data[r][1]['HC02_VC05'], data[r][2]['HC03_VC05'],
                                                data[r][0]['HC01_VC06'], data[r][1]['HC02_VC06'], data[r][2]['HC03_VC06'],
                                                data[r][0]['HC01_VC07'], data[r][1]['HC02_VC07'], data[r][2]['HC03_VC07'],
                                                data[r][0]['HC01_VC08'], data[r][1]['HC02_VC08'], data[r][2]['HC03_VC08'],
                                                data[r][0]['HC01_VC09'], data[r][1]['HC02_VC09'], data[r][2]['HC03_VC09'],
                                                data[r][0]['HC01_VC10'], data[r][1]['HC02_VC10'], data[r][2]['HC03_VC10'],
                                                data[r][0]['HC01_VC11'], data[r][1]['HC02_VC11'], data[r][2]['HC03_VC11'],
                                                data[r][0]['HC01_VC12'], data[r][1]['HC02_VC12'], data[r][2]['HC03_VC12'],
                                                data[r][0]['HC01_VC13'], data[r][1]['HC02_VC13'], data[r][2]['HC03_VC13'],
                                                data[r][0]['HC01_VC14'], data[r][1]['HC02_VC14'], data[r][2]['HC03_VC14'],
                                                track_pk_id))
                except:
                    pass
                self.acsdb.con.commit()


if __name__ == '__main__':
    pop = Populate()
    #pop.load_census_2010_zip_to_tracts()
    pop.load_tracts()
    #pop.load_S2503()
    #pop.load_geo_details()


