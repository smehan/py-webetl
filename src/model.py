# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
# -*- coding: UTF-8 -*-
from Pydb import Mysql
import pprint
import csv
import os

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
        """
        Builds up a data set of all tracts, including ratio to compute to each zip.
        :return:
        """
        self._get_zips()
        self._build_tracts()
        self._add_median_incomes()
        self._add_housing()
        self._add_occupancy_features()

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
        """
        builds up tract information in dataset, adding a track_pk_id, the ratio of
        residences of that tract to be counted in the chosen zip.
        :return:
        """
        with self.db.con.cursor() as cursor:
            for z in self.tracts:
                select_sql = "SELECT `track_pk_id`, `res_ratio` FROM `zip_tract_cw` " \
                             "WHERE `zip_pk_id`=%s"
                cursor.execute(select_sql, (self.tracts[z]['zip_pk_id']))
                ret = cursor.fetchall()
                for r in ret:
                    self.tracts[z][r['track_pk_id']] = {'res_ratio': r['res_ratio']}

    def _add_median_incomes(self):
        """
        builds median incomes for each tract, by occupied, owner-occupied, renter.
        :return:
        """
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
        """
        builds housing totals for occupied, owner-occupied, renter in each tract.
        :return:
        """
        with self.db.con.cursor() as cursor:
            for z in self.tracts:
                for k, v in self.tracts[z].items():
                    if k == 'zip_pk_id':
                        continue
                    select_sql = "SELECT `HC01_VC01`, `HC01_VC01_MOE`, " \
                                 "`HC02_VC01`, `HC02_VC01_MOE`, " \
                                 "`HC03_VC01`, `HC03_VC01_MOE` FROM `S2503_ACS` " \
                                 "WHERE `track_pk_id`=%s"
                    cursor.execute(select_sql, (k))
                    ret = cursor.fetchone()
                    if ret is not None:  # TODO: Flip this guard and warn in logger for None
                        self.tracts[z][k]['HC01_VC01'] = ret['HC01_VC01']
                        self.tracts[z][k]['HC02_VC01'] = ret['HC02_VC01']
                        self.tracts[z][k]['HC03_VC01'] = ret['HC03_VC01']
                        self.tracts[z][k]['HC01_VC01_MOE'] = ret['HC01_VC01_MOE']
                        self.tracts[z][k]['HC02_VC01_MOE'] = ret['HC02_VC01_MOE']
                        self.tracts[z][k]['HC03_VC01_MOE'] = ret['HC03_VC01_MOE']

    def _add_occupancy_features(self):
        """
        builds occupancy characteristics for occupied, owner-occupied, renter in each tract.
        :return: adds occupancy as sub-dict in self.tracts[z][tract_pk_id]
        """
        with self.db.con.cursor() as cursor:
            for z in self.tracts:
                for k, v in self.tracts[z].items():
                    if k == 'zip_pk_id':
                        continue
                    select_sql = "SELECT HC01_VC01, HC01_VC01_MOE, " \
                                 "HC02_VC01, HC02_VC01_MOE, " \
                                 "HC03_VC01, HC03_VC01_MOE, " \
                                 "HC01_VC03, HC01_VC03_MOE, " \
                                 "HC02_VC03, HC02_VC03_MOE, " \
                                 "HC03_VC03, HC03_VC03_MOE, " \
                                 "HC01_VC04, HC01_VC04_MOE, " \
                                 "HC02_VC04, HC02_VC04_MOE, " \
                                 "HC03_VC04, HC03_VC04_MOE, " \
                                 "HC01_VC05, HC01_VC05_MOE, " \
                                 "HC02_VC05, HC02_VC05_MOE, " \
                                 "HC03_VC05, HC03_VC05_MOE, " \
                                 "HC01_VC06, HC01_VC06_MOE, " \
                                 "HC02_VC06, HC02_VC06_MOE, " \
                                 "HC03_VC06, HC03_VC06_MOE, " \
                                 "HC01_VC14, HC01_VC14_MOE, " \
                                 "HC02_VC14, HC02_VC14_MOE, " \
                                 "HC03_VC14, HC03_VC14_MOE, " \
                                 "HC01_VC15, HC01_VC15_MOE, " \
                                 "HC02_VC15, HC02_VC15_MOE, " \
                                 "HC03_VC15, HC03_VC15_MOE, " \
                                 "HC01_VC19, HC01_VC19_MOE, " \
                                 "HC02_VC19, HC02_VC19_MOE, " \
                                 "HC03_VC19, HC03_VC19_MOE, " \
                                 "HC01_VC39, HC01_VC39_MOE, " \
                                 "HC02_VC39, HC02_VC39_MOE, " \
                                 "HC03_VC39, HC03_VC39_MOE " \
                                 "FROM S2501_ACS " \
                                 "WHERE track_pk_id=%s"
                    cursor.execute(select_sql, (k))
                    ret = cursor.fetchone()
                    if ret is not None:  # TODO: flip guard to None and output to logger
                        self.tracts[z][k]['occupancy'] = ret
                    else:
                        self.tracts[z][k]['occupancy'] = {}

    def build_rental_housing_densities(self):
        """
        calculates the density of renters/total occupied units in each zip.
        multiplies number of renters/occupiers by the weight of each tract contributing
        to the current zip.
        Firstly, get raw data for h1-4 renter numbers, and renters total units as well as total occupied
        units in tract. Get res_ratio, the fraction of that tract which is contributing to the present zip.
        Then normalize all of the h1-4 with the total renters to facilitate comparisons on same scale.
        If normalization is non-zero, calculate the normalized renter density for that group. Check to
        see if this is the max for the zip and store if so. Caclulate the contribution from this tract and
        add proportion element to total for the zip. Finally, calculate and store the avg for the zip.
        :return:
        """
        for z in self.tracts:
            t_rent = 0
            t_h1_rent = 0
            t_h2_rent = 0
            t_h3_rent = 0
            t_h4_rent = 0
            t_occ = 0
            self.tracts[z]['max_renter_density'] = self.tracts[z].get('max_renter_density', 0.0)
            self.tracts[z]['max_renter_income'] = self.tracts[z].get('max_renter_income', 0.0)
            self.tracts[z]['max_h1_renter_density'] = self.tracts[z].get('max_h1_renter_density', 0.0)
            self.tracts[z]['max_h2_renter_density'] = self.tracts[z].get('max_h2_renter_density', 0.0)
            self.tracts[z]['max_h3_renter_density'] = self.tracts[z].get('max_h3_renter_density', 0.0)
            self.tracts[z]['max_h4_renter_density'] = self.tracts[z].get('max_h4_renter_density', 0.0)
            for k,v in self.tracts[z].items():
                if isinstance(k, int):
                    renters = v.get('HC03_VC01', 0)
                    h1_renters = v['occupancy'].get('HC03_VC03', 0)
                    h2_renters = v['occupancy'].get('HC03_VC04', 0)
                    h3_renters = v['occupancy'].get('HC03_VC05', 0)
                    h4_renters = v['occupancy'].get('HC03_VC06', 0)
                    occupied = v.get('HC01_VC01', 1)
                    if v.get('res_ratio', 1) > 0:
                        res_ratio = v.get('res_ratio', 1)
                    else:
                        res_ratio = 1
                    if renters > 0:
                        current_den = renters/occupied
                    else:
                        current_den = 0.0
                    t_h_renters = h1_renters + h2_renters + h3_renters + h4_renters
                    if t_h_renters > 0:
                        ren_norm = renters/(t_h_renters)
                    else:
                        ren_norm = 1
                    h1_renters_norm = h1_renters*ren_norm
                    h2_renters_norm = h2_renters*ren_norm
                    h3_renters_norm = h3_renters*ren_norm
                    h4_renters_norm = h4_renters*ren_norm
                    if h1_renters_norm > 0:
                        current_h1_den = h1_renters_norm/occupied
                    else:
                        current_h1_den = 0.0
                    if h2_renters_norm > 0:
                        current_h2_den = h2_renters_norm/occupied
                    else:
                        current_h2_den = 0.0
                    if h3_renters_norm > 0:
                        current_h3_den = h3_renters_norm/occupied
                    else:
                        current_h3_den = 0.0
                    if h4_renters_norm > 0:
                        current_h4_den = h4_renters_norm/occupied
                    else:
                        current_h4_den = 0.0
                    if self.tracts[z]['max_renter_density'] < current_den:
                        self.tracts[z]['max_renter_density'] = round(current_den, 2)
                        self.tracts[z]['max_renter_income'] = round(v.get('HC03_VC14', 0.0), 0)
                    if self.tracts[z]['max_h1_renter_density'] < current_h1_den:
                        self.tracts[z]['max_h1_renter_density'] = round(current_h1_den, 2)
                    if self.tracts[z]['max_h2_renter_density'] < current_h2_den:
                        self.tracts[z]['max_h2_renter_density'] = round(current_h2_den, 2)
                    if self.tracts[z]['max_h3_renter_density'] < current_h3_den:
                        self.tracts[z]['max_h3_renter_density'] = round(current_h3_den, 2)
                    if self.tracts[z]['max_h4_renter_density'] < current_h4_den:
                        self.tracts[z]['max_h4_renter_density'] = round(current_h4_den, 2)
                    t_rent += renters * res_ratio
                    t_h1_rent += h1_renters_norm * res_ratio
                    t_h2_rent += h2_renters_norm * res_ratio
                    t_h3_rent += h3_renters_norm * res_ratio
                    t_h4_rent += h4_renters_norm * res_ratio
                    t_occ += occupied * res_ratio
            if t_rent == 0:
                self.tracts[z]['avg_renter_density'] = 0.0
            else:
                self.tracts[z]['avg_renter_density'] = round(t_rent/t_occ, 2)
            if t_h1_rent == 0:
                self.tracts[z]['avg_h1_renter_density'] = 0.0
            else:
                self.tracts[z]['avg_h1_renter_density'] = round(t_h1_rent/t_occ, 2)
            if t_h2_rent == 0:
                self.tracts[z]['avg_h2_renter_density'] = 0.0
            else:
                self.tracts[z]['avg_h2_renter_density'] = round(t_h2_rent/t_occ, 2)
            if t_h3_rent == 0:
                self.tracts[z]['avg_h3_renter_density'] = 0.0
            else:
                self.tracts[z]['avg_h3_renter_density'] = round(t_h3_rent/t_occ, 2)
            if t_h4_rent == 0:
                self.tracts[z]['avg_h4_renter_density'] = 0.0
            else:
                self.tracts[z]['avg_h4_renter_density'] = round(t_h4_rent/t_occ, 2)
        #self.make_output(output)
        #self.make_output(self.tracts, meth='pp')

    def build_incomes(self):
        """
        calculates the avg median renter income in each zip.
        multiplies number of renters by the weight of each tract contributing
        to the current zip.
        :return:
        """
        for z in self.tracts:
            t_rent_income = 0
            t_pop = 0
            self.tracts[z]['max_renter_density'] = self.tracts[z].get('max_renter_density', 0.0)
            self.tracts[z]['max_renter_income'] = self.tracts[z].get('max_renter_income', 0)
            for k,v in self.tracts[z].items():
                if isinstance(k, int):
                    income = v.get('HC03_VC14', 0)
                    pop = v.get('HC03_VC01', 0)
                    res_ratio = v.get('res_ratio', 1)
                    if res_ratio == 0: res_ratio = 1
                    t_rent_income += income * pop * res_ratio
                    t_pop += pop * res_ratio
            if t_pop == 0:
                self.tracts[z]['avg_renter_income'] = 0.0
            else:
                self.tracts[z]['avg_renter_income'] = round(t_rent_income/t_pop, 0)

    def build_model(self):
        """
        Builds up a derived dataset of relevant features from ACS info pulled or built in other methods.
        Purpose is specific to data needed for this particular output.
        :return:
        """
        output = []
        for z in self.tracts:
            line = [z]
            line.append(self.tracts[z].get('avg_renter_density', 0.0))
            line.append(self.tracts[z].get('max_renter_density', 0.0))
            line.append(self.tracts[z].get('avg_renter_income', 0))
            line.append(self.tracts[z].get('max_renter_income', 0))
            line.append(self.tracts[z].get('avg_h1_renter_density', 0))
            line.append(self.tracts[z].get('max_h1_renter_density', 0))
            line.append(self.tracts[z].get('avg_h2_renter_density', 0))
            line.append(self.tracts[z].get('max_h2_renter_density', 0))
            line.append(self.tracts[z].get('avg_h3_renter_density', 0))
            line.append(self.tracts[z].get('max_h3_renter_density', 0))
            line.append(self.tracts[z].get('avg_h4_renter_density', 0))
            line.append(self.tracts[z].get('max_h4_renter_density', 0))
            output.append(line)
        self.make_output(output, filename='model')

    def make_output(self, data, meth=None, filename=None):
        if meth == 'pp':
            pp = pprint.PrettyPrinter()
            pp.pprint(data)
            return
        elif filename is None:
            filename='output'
        dir_name='../data/output'
        filename_suffix = '.csv'
        path = os.path.join(dir_name, filename + filename_suffix)
        with open(path, 'w') as fh:
            writer = csv.writer(fh)
            for line in data:
                writer.writerow(line)

if __name__ == '__main__':
    myModel = Model()
    myModel.get_tracts()
    myModel.build_rental_housing_densities()
    myModel.build_incomes()
    myModel.build_model()
    myModel.make_output(data=myModel.tracts, meth='pp')
    myModel.destroy()