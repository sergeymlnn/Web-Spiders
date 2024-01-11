from typing import Iterator

from itemloaders.processors import MapCompose, TakeFirst
from scrapy import Spider as ScrapySpider
from scrapy.crawler import CrawlerProcess
from scrapy.http.response.html import HtmlResponse
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
# from scrapy.shell import inspect_response


class CarBrandItem(Item):
  """Item to collect info about car brands on the website"""
  brand: str = Field(output_processor=TakeFirst())
  quantity: int = Field(
    input_processor=MapCompose(lambda v: int(v.strip("()"))),
    output_processor=TakeFirst()
  )


# scrapy runspider main.py -o cars.json
class Spider(ScrapySpider):
  """Spider to collect info about car brands"""
  name = "auto_ria_spider"
  allowed_domains = "auto.ria.com"
  start_urls = ["https://auto.ria.com/uk/newauto/catalog/"]
  custom_settings = {
    "COOKIES_ENABLED": False,
    "DOWNLOAD_DELAY": 2,
    "ROBOTSTXT_OBEY": False,
    "LOG_LEVEL": "INFO",
  }

  def parse(self, response: HtmlResponse) -> Iterator[CarBrandItem]:
    """Extract info about car brands and the number of cars with such brands"""
    # inspect_response(response, self)
    brands = response.xpath("//a[@class='item-brands']/span[@class='top-brand']")
    if not brands:
      self.logger.critical("Brands were not found")
      return
    for brand in brands:
      item = ItemLoader(item=CarBrandItem(), selector=brand)
      item.add_xpath("brand", ".//span[@class='name']/text()")
      item.add_xpath("quantity", ".//span[@class='count']/text()")
      yield item.load_item()


if __name__ == '__main__':
  process = CrawlerProcess()
  process.crawl(Spider)
  process.start()
