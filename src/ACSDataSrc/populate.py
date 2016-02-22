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
                geo[r[1]] = [{'city': r[2]}, {'county': r[5]}, {'state': r[3]}, {'lat': r[9]}, {'lon': r[10]}]
        with self.acsdb.con.cursor() as cursor:
            for g in geo:
                update_sql = "INSERT INTO `zip` (`city`, `county`, `state`, `lat`, `lon`, `zipcode`) " \
                             "VALUES (%s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(update_sql, (geo[g][0]['city'],
                                                geo[g][1]['county'],
                                                geo[g][2]['state'],
                                                geo[g][3]['lat'],
                                                geo[g][4]['lon'],
                                                g))
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
                # name = re.search(r'[\w .]+', r[2]).group(0)
                r = [e.replace('-', '0') for e in r]
                r = [e.replace('(X)', '0') for e in r]
                r = [e.replace('250,000+', '250000') for e in r]
                r = [e.replace('***', '0') for e in r]
                r = [e.replace('**', '0') for e in r]
                data[r[1]] = [{'HC01_VC01': float(r[3])},
                              {'HC02_VC01': float(r[5])},
                              {'HC03_VC01': float(r[7])},
                              {'HC01_VC03': float(r[9])},
                              {'HC02_VC03': float(r[11])},
                              {'HC03_VC03': float(r[13])},
                              {'HC01_VC04': float(r[15])},
                              {'HC02_VC04': float(r[17])},
                              {'HC03_VC04': float(r[19])},
                              {'HC01_VC05': float(r[21])},
                              {'HC02_VC05': float(r[23])},
                              {'HC03_VC05': float(r[25])},
                              {'HC01_VC06': float(r[27])},
                              {'HC02_VC06': float(r[29])},
                              {'HC03_VC06': float(r[31])},
                              {'HC01_VC07': float(r[33])},
                              {'HC02_VC07': float(r[35])},
                              {'HC03_VC07': float(r[37])},
                              {'HC01_VC08': float(r[39])},
                              {'HC02_VC08': float(r[41])},
                              {'HC03_VC08': float(r[43])},
                              {'HC01_VC09': float(r[45])},
                              {'HC02_VC09': float(r[47])},
                              {'HC03_VC09': float(r[49])},
                              {'HC01_VC10': float(r[51])},
                              {'HC02_VC10': float(r[53])},
                              {'HC03_VC10': float(r[55])},
                              {'HC01_VC11': float(r[57])},
                              {'HC02_VC11': float(r[59])},
                              {'HC03_VC11': float(r[61])},
                              {'HC01_VC12': float(r[63])},
                              {'HC02_VC12': float(r[65])},
                              {'HC03_VC12': float(r[67])},
                              {'HC01_VC13': float(r[69])},
                              {'HC02_VC13': float(r[71])},
                              {'HC03_VC13': float(r[73])},
                              {'HC01_VC14': float(r[75])},
                              {'HC02_VC14': float(r[77])},
                              {'HC03_VC14': float(r[79])}]
        with self.acsdb.con.cursor() as cursor:
            for r in data:
                get_track_id_sql = "SELECT `pk_id` FROM `census_tract_2010` AS c WHERE `track_id`=%s"
                cursor.execute(get_track_id_sql, (r))
                track_pk_id = cursor.fetchone()
                if track_pk_id is None:
                    continue
                update_sql = "INSERT INTO `S2503_ACS` " \
                             "(`HC01_VC01`, `HC02_VC01`, `HC03_VC01`, " \
                             "`HC01_VC03`, `HC02_VC03`, `HC03_VC03`, " \
                             "`HC01_VC04`, `HC02_VC04`, `HC03_VC04`, " \
                             "`HC01_VC05`, `HC02_VC05`, `HC03_VC05`, " \
                             "`HC01_VC06`, `HC02_VC06`, `HC03_VC06`, " \
                             "`HC01_VC07`, `HC02_VC07`, `HC03_VC07`, " \
                             "`HC01_VC08`, `HC02_VC08`, `HC03_VC08`, " \
                             "`HC01_VC09`, `HC02_VC09`, `HC03_VC09`, " \
                             "`HC01_VC10`, `HC02_VC10`, `HC03_VC10`, " \
                             "`HC01_VC11`, `HC02_VC11`, `HC03_VC11`, " \
                             "`HC01_VC12`, `HC02_VC12`, `HC03_VC12`, " \
                             "`HC01_VC13`, `HC02_VC13`, `HC03_VC13`, " \
                             "`HC01_VC14`, `HC02_VC14`, `HC03_VC14`, " \
                             "`track_pk_id`) " \
                             "VALUES " \
                             "(%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s, %s, %s, " \
                             "%s)"
                try:
                    cursor.execute(update_sql, (data[r][0]['HC01_VC01'], data[r][1]['HC02_VC01'], data[r][2]['HC03_VC01'],
                                                data[r][3]['HC01_VC03'], data[r][4]['HC02_VC03'], data[r][5]['HC03_VC03'],
                                                data[r][6]['HC01_VC04'], data[r][7]['HC02_VC04'], data[r][8]['HC03_VC04'],
                                                data[r][9]['HC01_VC05'], data[r][10]['HC02_VC05'], data[r][11]['HC03_VC05'],
                                                data[r][12]['HC01_VC06'], data[r][13]['HC02_VC06'], data[r][14]['HC03_VC06'],
                                                data[r][15]['HC01_VC07'], data[r][16]['HC02_VC07'], data[r][17]['HC03_VC07'],
                                                data[r][18]['HC01_VC08'], data[r][19]['HC02_VC08'], data[r][20]['HC03_VC08'],
                                                data[r][21]['HC01_VC09'], data[r][22]['HC02_VC09'], data[r][23]['HC03_VC09'],
                                                data[r][24]['HC01_VC10'], data[r][25]['HC02_VC10'], data[r][26]['HC03_VC10'],
                                                data[r][27]['HC01_VC11'], data[r][28]['HC02_VC11'], data[r][29]['HC03_VC11'],
                                                data[r][30]['HC01_VC12'], data[r][31]['HC02_VC12'], data[r][32]['HC03_VC12'],
                                                data[r][33]['HC01_VC13'], data[r][34]['HC02_VC13'], data[r][35]['HC03_VC13'],
                                                data[r][36]['HC01_VC14'], data[r][37]['HC02_VC14'], data[r][38]['HC03_VC14'],
                                                track_pk_id['pk_id']))
                except Exception as e:
                    print(e)
                self.acsdb.con.commit()


if __name__ == '__main__':
    pop = Populate()
    #pop.load_census_2010_zip_to_tracts()
    #pop.load_tracts()
    pop.load_S2503()
    #pop.load_geo_details()


