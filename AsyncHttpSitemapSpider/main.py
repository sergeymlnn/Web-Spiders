import asyncio
from typing import Iterator, TypedDict

from httpx import AsyncClient, Response
from bs4 import BeautifulSoup, element


class CategoryItem(TypedDict):
  """Item to provide info about single category"""
  category: str
  description: str


async def log_response(response: Response) -> None:
  """
  Print info about received response from the website.

  :param response: response from the website
  """
  request = response.request
  print(f"Request {request.method} {response.url} - Status {response.status_code}")


async def parse_category(client: AsyncClient, url: str) -> CategoryItem:
  """
  Parse info about single category.

  :param client: async HTTP client
  :param url: URL to parse
  :return: info about single category
  """
  resp = await client.get(url)
  sp = BeautifulSoup(resp.text, "html.parser")
  category = sp.find("h1", id="page-title-heading").find_next().get_text(strip=True)
  description = sp.find("div", id="categoryDescription").get_text(strip=True)
  return CategoryItem(category=category, description=description)


async def parse_categories(client: AsyncClient, urls: Iterator[str]) -> list[str]:
  """
  Schedule tasks to parse info about all categories.

  :param client: async HTTP client
  :param urls: list of URLs to parse
  :return: info about all categories
  """
  tasks = (
    asyncio.create_task(parse_category(client, url))
    for url in urls
  )
  return await asyncio.gather(*tasks)


async def parse_xml_page(client: AsyncClient, url: str, limit: int) -> list[str]:
  """
  Parses XML-content extracting URLs inside <loc/> tags.

  :param client: async HTTP client
  :param url: URL to the XML-page with URLs to extract
  :param limit: total number of URLs to extract
  :return: list of URLs
  """
  resp = await client.get(url)
  sp = BeautifulSoup(resp.text, "xml")
  elements: list[element.Tag] = sp.find_all("loc", limit=limit)
  return [el.text for el in elements]


async def main() -> None:
  total_categories = 20
  url = "https://www.winfieldsoutdoors.co.uk/media/sitemapuk.xml"
  async with AsyncClient(event_hooks={"response": [log_response]}) as client:
    urls = await parse_xml_page(client, url, total_categories)
    categories = await parse_categories(client, urls)
  print(f"Extracted info about {len(categories)} categories")
  print(categories[1])


if __name__ == "__main__":
  asyncio.run(main())
