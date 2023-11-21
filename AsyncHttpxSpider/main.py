import asyncio
from typing import Any, Iterator

from httpx import AsyncClient, Response


async def log_response(response: Response) -> None:
  """Print info about received response from the server"""
  request = response.request
  print(f"Request {request.method} {response.url} - Status {response.status_code}")


async def parse_page(client: AsyncClient, url: str) -> dict[str, Any]:
  """Get JSON of a page"""
  resp = await client.get(url)
  return resp.json()


async def parse_pages(client: AsyncClient, urls: Iterator[str]) -> list[dict[str, Any]]:
  """Get JSON of all pages"""
  tasks = (
    asyncio.create_task(parse_page(client, url))
    for url in urls
  )
  return await asyncio.gather(*tasks)


async def main() -> None:
  """Run spider"""
  urls = (
    f"https://rickandmortyapi.com/api/character/{i}"
    for i in range(1, 51)
  )
  async with AsyncClient(event_hooks={"response": [log_response]}) as client:
    data = await parse_pages(client, urls)
  print(f"Received JSON of {len(data)} pages")


if __name__ == "__main__":
  asyncio.run(main())
