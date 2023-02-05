import scrapy
from scrapy import Selector

from pep_parse.items import PepParseItem


class PepSpider(scrapy.Spider):
    name = 'pep'
    allowed_domains = ['peps.python.org']
    start_urls = ['https://peps.python.org/']

    def parse(self, response):
        peps_table: Selector = response.css(
            "section[id='numerical-index']"
        ).css('tbody')[0]
        links = peps_table.css('a::attr(href)').getall()

        for link in links:
            yield response.follow(link, callback=self.parse_pep)

    def parse_pep(self, response):
        pep_info = response.css('section[id="pep-content"]')
        title = ''.join(
            response.xpath(
                '//*[@id="pep-content"]'
                '/h1'
                '//text()').getall())
        if title:
            number, name = title.split(' – ')
            data = {
                'number': int(number.replace('PEP ', '')),
                'name': name,
                'status': pep_info.css(
                    'dt:contains("Status") + dd abbr::text'
                ).get()
            }
            yield PepParseItem(data)
