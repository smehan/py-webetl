# Copyright (C) 2015-2016 Shawn Mehan <shawn dot mehan at shawnmehan dot com>
#
#  -*- coding: utf-8 -*-

import feedparser

d = feedparser.parse('http://feedparser.org/docs/examples/atom10.xml')
print(d['feed']['title'])