# -*- coding: utf-8 -*-

# Scrapy settings for folha_crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'folha_crawler'
LOG_LEVEL = 'INFO'
SPIDER_MODULES = ['folha_crawler.spiders']
NEWSPIDER_MODULE = 'folha_crawler.spiders'
ITEM_PIPELINES = ['folha_crawler.pipelines.FolhaCrawlerPipeline']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'folha_crawler (+http://www.yourdomain.com)'
