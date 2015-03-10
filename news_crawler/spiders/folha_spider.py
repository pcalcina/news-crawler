import re
import sys
from abstract_news_spider import AbstractNewsSpider

class FolhaSpider(AbstractNewsSpider):
    name         = 'folha-spider'
    initial_date = '01%2F01%2F2013'
    final_date   = '22%2F09%2F2014'
    url_template = ('http://busca.folha.uol.com.br/search?' +
                    'q=%s&site=%s&sd=%s&ed=%s&sr=%s')
    site         = 'jornal'
    source_id    = 2
    first_item   = 1
    #jornal = 2, online = 1

    def __init__(self):        
        super(FolhaSpider, self).__init__(
            'folha.uol.com.br', self.source_id, 'pro-life', r'protestos.sqlite')
    
    def get_total_articles(self, response):
        path = response.selector.css(".search-title > span").xpath('./node()')
        text = str(path[0].extract())
        return int(re.match(r".(\d+) - (\d+) de (\d+).", text).group(3))

    def get_article_links(self, response):
        css_path = '.search-results-list .search-results-title a'
#        css_path = '.search-results-title > a'
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
                                     
    
    def start_url(self):
         return self.url_template % (self.keywords, 
                                     self.site,
                                     self.initial_date, 
                                     self.final_date,
                                     self.first_item)
    
    def get_title(self, response):
        title = ''
        xpath_alternatives = [
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
                    break
         
        return date
