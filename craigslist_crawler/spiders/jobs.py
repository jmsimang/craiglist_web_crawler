# -*- coding: utf-8 -*-
import scrapy
import os
from scrapy.http import Request

class JobsSpider(scrapy.Spider):
    name = 'jobs'
    allowed_domains = ['capetown.craigslist.org']
    # start_urls = ['http://capetown.craigslist.org/']
    start_urls = ['https://capetown.craigslist.org/d/jobs/search/jjj']

    def parse(self, response):
        ''' Scrapy default function to parse the web content '''
        jobs = response.xpath('//li[@class="result-row"]')
        for job in jobs:
            date = job.xpath('.//*[@class="result-date"]/@datetime').extract_first()
            title = job.xpath('.//a[@class="result-title hdrlnk"]/text()').extract_first()
            link = job.xpath('.//a[@class="result-title hdrlnk"]/@href').extract_first()
            yield Request(link,
                          callback=self.parse_pages,
                          meta={'date': date,
                                'link': link,
                                'title': title})

        next_url_page = response.xpath('//a[@class="button next"]/@href').extract_first()
        if next_url_page:
            absolute_next_page_url = response.urljoin(next_url_page)
            yield Request(absolute_next_page_url, callback=self.parse)

    def parse_pages(self, response):
        ''' Unpack data points from parse function '''
        date = response.meta['date']
        title = response.meta['title']
        link = response.meta['link']

        compensation = response.xpath('//*[@class="attrgroup"]/span[1]/b/text()').extract_first()
        emp_type = response.xpath('//*[@class="attrgroup"]/span[2]/b/text()').extract_first()
        images = response.xpath('//*[@id="thumbs"]//@src').extract()
        if images:
            images = [image.replace('50x50c', '600x450') for image in images]
        description = response.xpath('//*[@id="postingbody"]/text()').extract()

        yield {
            'date': date,
            'title': title,
            'link': link,
            'compensation': compensation,
            'emp_type': emp_type,
            'images': images,
            'description': description,
        }
