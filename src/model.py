# -*- coding: UTF-8 -*-
from Pydb import Mysql
import pprint
import csv

class Model():
    """

    """

    def __init__(self):
        """Constructor for Model"""
        self.db = Mysql("Pydb/mysql_config.yml")
        self.tracts = {}

    def destroy(self):
        self.db.exit()

    def get_tracts(self):
        self._get_zips()
        self._build_tracts()
        self._add_median_incomes()
        self._add_housing()

    def _get_zips(self):
        """
        returns all the Nassau county pk_ids of zips, sorted by city asc
        :param self:
        :return:
        """
        with self.db.con.cursor() as cursor:
            select_sql = "SELECT `pk_id`,`zipcode` FROM zip WHERE `county`=%s " \
                         "ORDER BY `city` ASC"
            cursor.execute(select_sql, ("Nassau"))
            ret = cursor.fetchall()
            for r in ret:
                self.tracts[r['zipcode']] = {'zip_pk_id': r['pk_id']}

    def _build_tracts(self):
        with self.db.con.cursor() as cursor:
            for z in self.tracts:
                select_sql = "SELECT `track_pk_id`, `res_ratio` FROM `zip_tract_cw` " \
                             "WHERE `zip_pk_id`=%s"
                cursor.execute(select_sql, (self.tracts[z]['zip_pk_id']))
                ret = cursor.fetchall()
                for r in ret:
                    self.tracts[z][r['track_pk_id']] = {'res_ratio': r['res_ratio']}

    def _add_median_incomes(self):
        with self.db.con.cursor() as cursor:
            for z in self.tracts:
                for k,v in self.tracts[z].items():
                    if k == 'zip_pk_id':
                        continue
                    select_sql = "SELECT `HC01_VC14`, `HC02_VC14`, `HC03_VC14` FROM `S2503_ACS` " \
                                 "WHERE `track_pk_id`=%s"
                    cursor.execute(select_sql, (k))
                    ret = cursor.fetchone()
                    if ret is not None:
                        self.tracts[z][k]['HC01_VC14'] = ret['HC01_VC14']
                        self.tracts[z][k]['HC02_VC14'] = ret['HC02_VC14']
                        self.tracts[z][k]['HC03_VC14'] = ret['HC03_VC14']

    def _add_housing(self):
        with self.db.con.cursor() as cursor:
            for z in self.tracts:
                for k,v in self.tracts[z].items():
                    if k == 'zip_pk_id':
                        continue
                    select_sql = "SELECT `HC01_VC01`, `HC02_VC01`, `HC03_VC01` FROM `S2503_ACS` " \
                                 "WHERE `track_pk_id`=%s"
                    cursor.execute(select_sql, (k))
                    ret = cursor.fetchone()
                    if ret is not None:
                        self.tracts[z][k]['HC01_VC01'] = ret['HC01_VC01']
                        self.tracts[z][k]['HC02_VC01'] = ret['HC02_VC01']
                        self.tracts[z][k]['HC03_VC01'] = ret['HC03_VC01']

    def build_densities(self):
        output = []
        for z in self.tracts:
            t_den = 0
            count = 0
            for k,v in self.tracts[z].items():
                if k == 'zip_pk_id':
                    continue
                if 'HC03_VC01' not in v or 'HC01_VC01' not in v or 'res_ratio' not in v:
                    print("Insufficient data for renter density for %s: %s" % (z, k))
                    continue
                if v['HC01_VC01'] == 0:
                    continue  # no housing in this tract
                if v['res_ratio'] == 0:
                    v['res_ratio'] = 1.0
                t_den += v['HC03_VC01']/v['HC01_VC01'] * v['res_ratio']
                count += 1
                output.append([v['HC03_VC01']/v['HC01_VC01'], v['HC03_VC01'], v['HC01_VC01'], z])
            if count != 0:
                density = t_den/count
                self.tracts[z]['renter_density'] = density
        self.make_output(output)


    def make_output(self, data, meth=None):
        if meth == 'pp':
            pp = pprint.PrettyPrinter()
            pp.pprint(self.tracts)
        else:
            with open("../data/output/output.csv", 'w') as fh:
                writer = csv.writer(fh)
                for line in data:
                    writer.writerow(line)

if __name__ == '__main__':
    myModel = Model()
    myModel.get_tracts()
    myModel.build_densities()
    #myModel.output()
    myModel.destroy()