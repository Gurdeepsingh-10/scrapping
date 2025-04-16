from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    CrawlerMonitor,
    MemoryAdaptiveDispatcher
)
import asyncio


async def crawl_batch():
    browserconfig = BrowserConfig(headless=True, verbose=False)

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        check_robots_txt=True,
        stream=False
    )

    monitor = CrawlerMonitor()  # No display_mode

    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=10,
        monitor=monitor
    )

    urls = [
        "https://www.codingwithroby.com/",
        "https://www.codingwithroby.com/about",
        "https://www.codingwithroby.com/courses",
        "https://www.codingwithroby.com/freebies",
    ]

    async with AsyncWebCrawler(config=browserconfig) as crawler:
        results = await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher
        )

        for result in results:
            if result.success:
                await process_result(result)
            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")


async def process_result(result):
    print(f"\nProcessing: {result.url}")
    print(f"Status Code: {result.status_code}")

    if result.markdown:
        clean_text = ' '.join(result.markdown.split())
        preview = clean_text[:150] + "..." if len(clean_text) > 150 else clean_text
        print(f"Content Preview: {preview}")

    if result.metadata:
        print("\nMetadata:")
        for key, value in result.metadata.items():
            print(f"  {key}: {value}")

    if result.links:
        internal_links = result.links.get("internal", [])
        external_links = result.links.get("external", [])
        print(f"Found {len(internal_links)} internal links")
        print(f"Found {len(external_links)} external links")

    print("-" * 80)


asyncio.run(crawl_batch())
