import re
import sys
import logging
from abstract_news_spider import AbstractNewsSpider

class FolhaSpider(AbstractNewsSpider):
    name         = 'folha-spider'
    url_template = ('http://busca.folha.uol.com.br/search?' +
                    'q=%s&site=%s&sd=%s&ed=%s&sr=%s')
    site         = 'todos'
    source_id    = 2
    first_item   = 1
    initial_date = ''
    final_date   = ''

    def __init__(self, 
                 keywords     = '', 
                 initial_date = '01%2F01%2F2013', 
                 final_date   = '22%2F09%2F2014'):        
        super(FolhaSpider, self).__init__( 'folha.uol.com.br',
                                           self.source_id,
                                           r'protestos.sqlite',
                                           keywords,
                                           self.start_url(keywords,
                                                          initial_date, final_date))
        self.initial_date = initial_date
        self.final_date   = final_date
        logging.info('FolhaSpider: INITIAL:%s, END:%s' %(self.initial_date, self.final_date))
    
    def get_total_articles(self, response):
        path = response.selector.css(".search-title > span").xpath('./node()')
        text = str(path[0].extract())
        return int(re.match(r".(\d+) - (\d+) de (\d+).", text).group(3))

    def get_article_links(self, response):
        css_path = '.search-results-list .search-results-title a'
        return response.selector.css(css_path)
        
    def get_body(self, response):
        selector = '.article [itemprop=articleBody]'
        items = response.selector.css(selector).xpath('./node()').extract()
        if len(items) == 0:
            selector = '#articleNew'
            items = response.selector.css(selector).xpath('./node()').extract()
        return ' '.join(items)
    
    def get_next_page_url(self):
        next_item = self.next_page*self.items_per_page + 1
        url = self.url_template % (self.keywords, 
                                   self.site,
                                   self.initial_date, 
                                   self.final_date,
                                   next_item)
        return url
                                     
    
    def start_url(self, keywords, initial_date, final_date):
        initial_url = self.url_template % (keywords, 
                                     self.site,
                                     initial_date, 
                                     final_date,
                                     self.first_item)
        logging.info('Returning initial url: %s' %(initial_url))
        return initial_url
    
    def get_title(self, response):
        title = 'NO TITLE'
        xpath_alternatives = [
            '//article/header/h1/text()',
            '//html/body/meta[@itemprop="alternativeHeadline"]/@content',
            '//html/head/meta[@name="title"]/@content',
            '//div[@id="articleNew"]/h1/text()',
            '//p[@class="title"]/text()']
        for xpath in xpath_alternatives:            
            items = response.xpath(xpath).extract()
            if items:
                title = items[0]
                break        
        return title
        
    def format_date(self, date_text):
        date = None
        matches = re.match('(\d{2})/(\d{2})/(\d{4}).*', date_text)
        if matches:
            (dd, mm, yy) = matches.groups()
            date = '%s-%s-%s' % (yy, mm, dd)
        else:
            matches = re.match('(\d{4}-\d{2}-\d{2}).*', date_text)
            if matches:
                date = matches.group(0)
        return date

    def get_date(self, response):
        xpath_alternatives = [
            '//div[@id="articleNew"]/p[@class="publish"]/text()',
            '//article/header/time/text()',
            '//html/body/meta[@itemprop="datePublished"]/@content',
            '//div[@id="articleDate"]/text()',
            '//html/head/meta[@name="date"]/@content']
        date = 'No date'
        for xpath in xpath_alternatives:
            items = response.xpath(xpath).extract()
            if items:
                text  = ' '.join(items).strip()
                date_candidate = self.format_date(text)
                if date_candidate:
                    date = date_candidate
                    print "A data escolhida date=%s, xpath=%s" % (date, xpath)
                    break
        return date
