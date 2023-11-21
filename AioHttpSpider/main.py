import asyncio
from typing import Iterator

from aiohttp import ClientSession


async def parse_page(session: ClientSession, url: str) -> str:
  """Get HTML of a page"""
  print(f"Processing {url}")
  async with session.get(url) as resp:
    return await resp.text()


async def parse_pages(session: ClientSession, urls: Iterator[str]) -> list[str]:
  """Get HTML of all pages"""
  tasks = (
    asyncio.create_task(parse_page(session, url))
    for url in urls
  )
  return await asyncio.gather(*tasks)


async def main() -> None:
  """Run spider"""
  urls = (
    f"https://books.toscrape.com/catalogue/page-{i}.html"
    for i in range(1, 51)
  )
  async with ClientSession() as session:
    data = await parse_pages(session, urls)
  print(f"Received HTML of {len(data)} pages")


if __name__ == "__main__":
  asyncio.run(main())
