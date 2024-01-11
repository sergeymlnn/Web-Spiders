from typing import Dict, Iterator

from scrapy import Spider as ScrapySpider
from scrapy.crawler import CrawlerProcess
from scrapy.http.response import Response
from scrapy.selector.unified import Selector
from scrapy.utils.gz import gunzip
# from scrapy.shell import inspect_response


# scrapy runspider main.py -o urls.json
class Spider(ScrapySpider):
  """Spider to extract URLs from Gzipped content"""
  name = "alternate_de_spider"
  allowed_domains = ["alternate.de"]
  start_urls = [
    "https://www.alternate.de/sitemap_article1.xml.gz",
    "https://www.alternate.de/sitemap_article2.xml.gz",
  ]
  custom_settings = {
    "COOKIES_ENABLED": False,
    "ROBOTSTXT_OBEY": False,
  }

  def parse(self, response: Response) -> Iterator[Dict[str, str]]:
    """Extract URLs from Gzipped content"""
    text = gunzip(response.body).decode("utf-8")
    selector = Selector(text=text)
    urls = selector.xpath("//url/loc/text()").getall()
    for url in urls:
      yield {"url": url}


if __name__ == '__main__':
  process = CrawlerProcess()
  process.crawl(Spider)
  process.start()
