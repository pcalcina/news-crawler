import abc
import math
import os
import re
import scrapy
import sqlite3
import sys

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from news_crawler.items import NewsItem

class AbstractNewsSpider(CrawlSpider):
    __metaclass__       = abc.ABCMeta
    name                = 'abstract-news-spider'
    final_page          = None
    next_page           = 0
    items_per_page      = 25
    title_pages         = {}
    keywords            = ''
    conn                = None
    accept_new_articles = True
    
    def __init__(self, domain, source_id, database, keywords):
        self.allowed_domains = [domain]            
        self.source_id       = source_id
        self.keywords        = keywords
        self.start_urls      = [self.start_url()]
        self.conn            = sqlite3.connect(database)
        self.cursor          = self.conn.cursor()
        
    def parse(self, response):
        if self.final_page is None:
            total = self.get_total_articles(response)
            self.final_page = int(math.ceil(float(total) / 
                                  self.items_per_page))
            self.next_page = 1
        
        if self.has_more_pages():
            i = 0
            for article_link in self.get_article_links(response):                
                i += 1
                url = self.get_url(article_link)
                if url:                
                    if self.already_crawled(url):
                        print '[%d-2%d MERGING OLD] %s' % (self.next_page, i, url)
                        self.merge_keywords(url)
                    elif self.accept_new_articles:
                        print '[%d-2%d ADDING NEW] %s' % (self.next_page, i, url)
                        try:
                            yield scrapy.Request(str(url), 
                                             callback=self.parse_article)
                        except Exception as e:
                            print ('ERROR trying to crawling %s. Message=%s' % 
                                   (url, e))
                    else:
                        print '[%d-2%d SKIPPING NEW] %s' % (self.next_page, i, url)
            yield scrapy.Request(self.get_next_page_url(), callback=self.parse)
            self.next_page += 1
            
    @abc.abstractmethod
    def start_url(self):
         """Returns the url to begin the crawling."""

    @abc.abstractmethod
    def get_total_articles(self):
        """Returns the number of results for the given search."""
        
    @abc.abstractmethod
    def get_article_links(self, response):
        """Returns the list of link to news articles for the current 
           page of the search result."""
           
    @abc.abstractmethod
    def get_date(self, response):
        """Returns the date of the news article."""
           
    @abc.abstractmethod
    def get_body(self, response):
        """Returns the body of the news article."""

    @abc.abstractmethod
    def get_title(self, response):
        """Returns the title of th news article."""
        
    @abc.abstractmethod
    def get_next_page_url(self):
        """Return the URL of the next page to crawl."""

    def parse_article(self, response):
        print " **** RECEIVING %s ti save **** " % (str(response))
        item = NewsItem()
        item['date']      = self.get_date(response)
        item['body']      = self.get_body(response)
        item['title']     = self.get_title(response)
        item['link']      = self.get_url_suffix(response.url)
        item['source_id'] = self.source_id
        item['keywords']  = self.keywords
        return item

    def already_crawled(self, url):
        self.cursor.execute(
            'SELECT count(*) AS total FROM news WHERE news.url_suffix = ?',
            [self.get_url_suffix(url)])
        [total] = self.cursor.fetchone()
        print "Verifying if %s URL is crawled, total = %d" % (url, total)
        return total > 0
    
    def merge_keywords(self, url):
        self.cursor.execute('SELECT news_id, keywords FROM news WHERE news.url_suffix = ?',
                       [self.get_url_suffix(url)])
        [news_id, keywords] = self.cursor.fetchone()
        keywords_list = keywords.split(',')
        keywords_list.append(self.keywords)
        new_keywords = ','.join(sorted(set(keywords_list)))
        self.cursor.execute('''UPDATE news SET keywords = ? WHERE news_id = ?''', 
                       [new_keywords, news_id])
        print(new_keywords);
        self.conn.commit()

    def has_more_pages(self):
        print ' --- Page %s of %s --- ' % (self.next_page, self.final_page)
        return self.next_page <= self.final_page
    
    def get_url(self, article_link):
        return article_link.xpath('./@href').extract()[0]
        
    def get_url_suffix(self, url):
        try:
            suffix = url.split(self.allowed_domains[0])[1]
        except:
            suffix = url
        return suffix

