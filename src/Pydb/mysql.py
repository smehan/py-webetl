# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
#  -*- coding: UTF-8 -*-
"""
Class for creating a db object that connects to a defined mysql instance and
permits various cursor executions. Uses PyMysql as the DBI driver. This is not the
pip PyMysql3 which is an older version of said.
"""

import pymysql.cursors
import yaml


class Mysql():
    def __init__(self, path):
        """
        :param path: the path to the config file for this particular mysql db connection
        :return: an initiated db object connected to a schema in a mysql instance
        """

        with open(path, 'r') as fh:
            settings = yaml.load(fh)

        self.db_host = settings['DB_HOST']
        self.db_user = settings['DB_USER']
        self.db_passwd = settings['DB_PASSWD']
        self.db_name = settings['DB_NAME']

        # connect to the database specified in the config file
        self.con = pymysql.connect(host=self.db_host,
                                   user=self.db_user,
                                   password=self.db_passwd,
                                   db=self.db_name,
                                   charset='utf8mb4',
                                   cursorclass=pymysql.cursors.DictCursor)

    def insert(self, values):
        try:
            with self.con.cursor() as cursor:
                sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
                cursor.execute(sql, (values[0], values[1]))
                self.con.commit()
        except:
            pass

    def read(self):
        try:
            with self.con.cursor() as cursor:
                sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
                cursor.execute(sql, ('v1',))
                result = cursor.fetchone()
                print(result)
        except:
            pass

    def exit(self):
        self.con.close()

if __name__ == '__main__':
    testdb = Mysql("mysql_config.yaml")
    testdb.insert(['v1', 'v2'])
    testdb.read()
    testdb.exit()