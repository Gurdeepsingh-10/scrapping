import asyncio
import time
import psutil
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    CrawlerMonitor,
    MemoryAdaptiveDispatcher
)

console = Console()
process = psutil.Process()


async def crawl_batch():
    browserconfig = BrowserConfig(headless=True, verbose=False)

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        check_robots_txt=True,
        stream=False
    )

    monitor = CrawlerMonitor()  # Base monitor

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

    start_time = time.time()

    async with AsyncWebCrawler(config=browserconfig) as crawler:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            transient=True,
        ) as progress:

            task = progress.add_task("Crawling pages...", total=len(urls))
            results = await crawler.arun_many(
                urls=urls,
                config=run_config,
                dispatcher=dispatcher
            )
            progress.update(task, advance=len(results))

        total_time = time.time() - start_time
        mem_mb = process.memory_info().rss / 1024 / 1024

        # Display performance metrics in a table
        table = Table(title="Crawl Performance Summary", show_lines=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Total URLs Crawled", str(len(urls)))
        table.add_row("Total Time (s)", f"{total_time:.2f}")
        table.add_row("Memory Usage (MB)", f"{mem_mb:.2f}")

        console.print(table)

        for result in results:
            if result.success:
                await process_result(result)
            else:
                console.print(f"[red]❌ Failed to crawl[/red] {result.url}: {result.error_message}")


async def process_result(result):
    console.print(f"\n[bold green]✔ Processing:[/bold green] {result.url}")
    console.print(f"Status Code: {result.status_code}")

    if result.markdown:
        clean_text = ' '.join(result.markdown.split())
        preview = clean_text[:150] + "..." if len(clean_text) > 150 else clean_text
        console.print(f"[blue]Content Preview:[/blue] {preview}")

    if result.metadata:
        console.print("\n[bold]Metadata:[/bold]")
        for key, value in result.metadata.items():
            console.print(f"  {key}: {value}")

    if result.links:
        internal_links = result.links.get("internal", [])
        external_links = result.links.get("external", [])
        console.print(f"🔗 Found {len(internal_links)} internal links")
        console.print(f"🌍 Found {len(external_links)} external links")

    console.print("-" * 80)


asyncio.run(crawl_batch())
