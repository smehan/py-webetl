# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
#  -*- coding: utf-8 -*-

from amazon.api import AmazonAPI
import yaml


class AZ(object):
    def __init__(self):

        with open("az_config.yaml", "r") as f:
            settings = yaml.load(f)

        self.access_key = settings['access_key_id']
        self.secret_key = settings['secret_key_id']
        self.associate_tag = settings['associate_tag']
        self.az_price = None
        self.az_asin = None
        self.az_weight = None
        self.az_sales_rank = None
        self.az_url = None

        self.amazon = AmazonAPI(self.access_key, self.secret_key, self.associate_tag)

    def find_best_match(self, title, cat='All'):
        self._find_by_title(title, cat)
        self._get_attrs()
        return self.az_price, self.az_weight, self.az_sales_rank, self.az_url

    def _find_by_title(self, title, cat):
        lowest = 0.0
        try:
            products = self.amazon.search(Title=title, SearchIndex=cat)
            for i,p in enumerate(products):
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
            except:
                pass
            if r is None:
                r = 0
            if w is None:
                w = 0
            else:
                w = float(w)*0.01  # its coming from amazon in hundreth-pounds seemingly
        else:  # there was no product found.
            r, w = 0
            u = None
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
                w = None
            if w is None:
                w = 0
            else:
                w = float(w)*0.01  # its coming from amazon in hundreth-pounds seemingly
        else:
            w = 0
        return w

