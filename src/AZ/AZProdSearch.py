# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
#  -*- coding: utf-8 -*-

from amazon.api import AmazonAPI
from HTTPUtils import get_page
import yaml
import os
from loggerUtils import init_logging
from Pydb import Mysql
import logging
import re
import datetime


class AZ(object):
    def __init__(self):
        init_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Amazon object initialized")

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "az_config.yml"), "r") as fh:
            settings = yaml.load(fh)

        self.db = Mysql(settings['db_config'])

        self.access_key = settings['access_key_id']
        self.secret_key = settings['secret_key_id']
        self.associate_tag = settings['associate_tag']
        self.product = {}
        self.az_price = None
        self.az_asin = None
        self.az_weight = settings['default_weight']
        self.az_sales_rank = None
        self.az_url = None
        self.az_match = None

        self.amazon = AmazonAPI(self.access_key, self.secret_key, self.associate_tag)

    def destroy(self):
        self.logger.info("Database connection closed...")
        self.db.exit()
        self.logger.info("Amazon object destroyed")

    def find_best_match(self, title, cat='All'):  # TODO: consider using cat='Blended' for default
        """

        :param title: string containing the source site product title
        :param cat: string containing the category for searchindex on amazon
        :return: price, weight, sales_rank, offer_url and T if match occurred on title search,
        K if match occurred on keyword search, N if no match occurred.
        """
        self._find_by_title(title, cat)
        if self.az_price != 0:
            self.az_match = 'T'
        if self.az_price == 0:
            self._find_by_key(title, cat)
            if self.az_price != 0:
                self.az_match = 'K'
        if self.az_price == 0:  # we didn't find any match so clean remaining attrs
            (self.az_sales_rank, self.az_match, self.az_url) = (0, 'N', '')
        self._get_attrs()
        return self.az_price, self.az_weight, self.az_sales_rank, self.az_match, self.az_url, self.az_asin

    def _find_by_title(self, title, cat):
        lowest = 0.0
        try:
            products = self.amazon.search(Title=title, SearchIndex=cat)
            for i, p in enumerate(products):
                price = p.price_and_currency[0]
                if lowest == 0.0:
                    lowest = price
                    self.az_asin = p.asin
                elif price < lowest:
                    lowest = price
                    self.az_asin = p.asin
        except Exception as e:
            pass
        self.az_price = lowest

    def _find_by_key(self, title, cat):
        lowest = 0.0
        try:
            products = self.amazon.search(Keywords=title, SearchIndex=cat)
            for i, p in enumerate(products):
                price = p.price_and_currency[0]
                if lowest == 0.0:
                    lowest = price
                    self.az_asin = p.asin
                elif price < lowest:
                    lowest = price
                    self.az_asin = p.asin
        except Exception as e:
            pass
        self.az_price = lowest

    def _get_attrs(self):
        (r, w, u) = (None, None, None)
        if self.az_asin is not None:
            try:
                p = self.amazon.lookup(ItemId=self.az_asin)
                r = int(p.sales_rank)
                w = p.get_attribute('ItemDimensions.Weight')
                u = p.offer_url
                self._get_meta_rate(p.reviews[1])
            except:
                pass
            if r is None:
                r = 0
            if w is None:
                w = self.az_weight  # this should not be in hundreth-pounds
            else:
                w = float(w)*0.01  # its coming from amazon in hundreth-pounds seemingly
        else:  # there was no product found.
            (r, w, u) = (0, 0, '')
        self.az_sales_rank = r
        self.az_weight = w
        self.az_url = u

    def _get_weight(self):
        w = None
        if self.az_asin is not None:
            try:
                p = self.amazon.lookup(ItemId=self.az_asin)
                w = p.get_attribute('ItemDimensions.Weight')
            except:
                pass
            if w is None:
                w = self.az_weight
            else:
                w = float(w)*0.01  # its coming from amazon in hundreth-pounds seemingly
        else:
            w = 0
        return w

    def _get_meta_rate(self, url):
        rank_page = get_page(url, 1)
        if rank_page[0].find(string=re.compile(r'There are no customer reviews for this item')):
            self.product['num_reviews'] = 0
            self.product['avg_review'] = 0
        else:
            try:
                rating = rank_page[0].find("span", {"class":"asinReviewsSummary"}).img.attrs['title']
                self.product['num_reviews'] = rating
            except:
                self.product['num_reviews'] = 0
            try:
                reviews = rank_page[0].find(string=re.compile(r'\d+ customer reviews'))
                self.product['avg_review'] = reviews
            except:
                self.product['avg_review'] = 0

    def match_products(self):
        self._get_unmatched_products()

    def _get_unmatched_products(self):
        products = {}
        with self.db.con.cursor() as cursor:
            select_sql = "SELECT pk_id " \
                         "FROM match_cw " \
                         "WHERE az_pk_id=%s"
            try:
                cursor.execute(select_sql, (""))
                ret = cursor.fetchall()
                print(ret)
            except Exception as e:
                self.logger.exception(e)

    def _persist_match(self, match):
        if match is None:
            return
        with self.db.con.cursor() as cursor:
            select_sql = "SELECT pk_id " \
                         "FROM match_cw " \
                         "WHERE pk_id=%s"
            cursor.execute(select_sql, (match['pk_id']))
            ret = cursor.fetchone()
            if ret is None:
                self.logger.warn("There was a match issue with az_pk_id %s" % match['pk_id'])
                return
            update_sql = "UPDATE match_cw " \
                         "SET az_pk_id=%s, wal_pk_id=%s, " \
                         "net=%s, roi=%s, match_score=%s, " \
                         "match_meth=%s, last_update=now() " \
                         "WHERE pk_id=%s"
            cursor.execute(update_sql, (match['az_pk_id'],
                                        match['wal_pk_id'],
                                        match['net'],
                                        match['roi'],
                                        match['match_score'],
                                        match['match_meth'],
                                        match['pk_id']))
            self.db.con.commit()

    def _persist_product(self, product):
        """
        This method will insert or update a row for the product in the az table as well
        as update the corresponding row in match_cw with the az_pk_id. Expects
        to find az_product with asin.
        If a match_cw_id is passed, then there is a row in match_cw that needs to be updated
        with the product asin.
        :param product: dictionary with values to insert/update in az_product.
        :return:
        """
        if 'name' not in product:
            self.logger.warn("Attempt to persist empty product!")
            return
        with self.db.con.cursor() as cursor:
            select_sql = "SELECT pk_id, price " \
                         "FROM az_product " \
                         "WHERE asin=%s"
            cursor.execute(select_sql, (product['asin']))
            ret = cursor.fetchone()
            if ret is None:
                insert_sql = "INSERT INTO az_product " \
                             "(asin, avg_rate, img, num_reviews, " \
                             "price, sales_rank, shipping_cost, " \
                             "title, upc, url, weight, " \
                             "last_read, last_changed) " \
                             "VALUES " \
                             "(%s, %s, %s, %s, %s, %s, %s)"
                try:
                    cursor.execute(insert_sql, (product['asin'],
                                                product['avg_rate'],
                                                product['img'],
                                                product['num_reviews'],
                                                product['price'],
                                                product['sales_rank'],
                                                product['shipping_cost'],
                                                product['title'],
                                                product['url'],
                                                product['weight'],
                                                datetime.datetime.now(),
                                                datetime.datetime.now()))
                    self.db.con.commit()
                except:
                    self.logger.exception('Failed to insert new az product: %s.' % product['asin'])
            elif product['price'] != ret['price']:
                update_sql = "UPDATE az_product " \
                             "SET asin=%s, avg_rate=%s, " \
                             "img=%s, num_reviews=%s, " \
                             "price=%s, sales_rank=%s, " \
                             "shipping_cost=%s, last_read=now(), " \
                             "last_changed=now(), title=%s, " \
                             "url=%s, weight=%s " \
                             "WHERE pk_id=%s"
                try:
                    cursor.execute(update_sql, (product['price'],
                                                product['title'],
                                                product['url'],
                                                product['img'],
                                                ret['pk_id']))
                    self.db.con.commit()
                except:
                    self.logger.exception('Failed to update az product: %s.' % product['asin'])
            else:
                update_sql = "UPDATE az_product " \
                             "SET last_read=now()" \
                             "WHERE pk_id=%s"
                cursor.execute(update_sql, (ret['pk_id']))
                self.db.con.commit()
            if product.get('match'):
                self._persist_match(product['match'])

if __name__ == '__main__':
    az = AZ()
    az.match_products()
    az.destroy()