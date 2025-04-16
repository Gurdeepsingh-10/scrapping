import asyncio
from crawl4ai import AsyncWebCrawler


async def main():
    async with AsyncWebCrawler () as crawler :
        result = await crawler.arun("https://www.codingwithroby.com/")
        print(result.markdown)


asyncio.run(main())