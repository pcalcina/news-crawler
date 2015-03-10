# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class NewsItem(scrapy.Item):
    title     = scrapy.Field()
    link      = scrapy.Field()
    body      = scrapy.Field()
    date      = scrapy.Field()
    source_id = scrapy.Field()
    keywords  = scrapy.Field()

class NewsQueue(scrapy.Item):
    link = scrapy.Field()

