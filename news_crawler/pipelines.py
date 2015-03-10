# -*- coding: utf-8 -*-
import sqlite3
import re

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class FolhaCrawlerPipeline(object):

    def process_item(self, item, spider):
        domain = 'http://www.folha.uol.com.br'
        conn = sqlite3.connect('protestos.sqlite')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO news(title, content, date, url, url_suffix, source_id, keywords)
                   VALUES(?,?,?,?,?,?,?)''', (item['title'], item['body'], 
                  item['date'], domain + item['link'], item['link'], item['source_id'], item['keywords']))
                  
        conn.commit()
        cursor.close()
        
        return item
