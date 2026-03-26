import argparse
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def fetch_duckduckgo(query: str, page: int) -> List[str]:
    """DuckDuckGo HTML endpoint (~30 results per page)."""
    params = {
        "q": query,
        "s": (page - 1) * 30,
    }
    resp = requests.get(
        "https://duckduckgo.com/html/",
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    anchors = soup.select("a.result__a, a.result__url")
    return [a.get("href") for a in anchors if a.get("href")]


def fetch_bing(query: str, page: int) -> List[str]:
    """Bing HTML results (used by Edge)."""
    params = {
        "q": query,
        "first": (page - 1) * 10 + 1,
    }
    resp = requests.get(
        "https://www.bing.com/search",
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    anchors = soup.select("li.b_algo h2 a, a.tilt")
    return [a.get("href") for a in anchors if a.get("href")]


def fetch_brave(query: str, page: int) -> List[str]:
    """Brave search HTML results."""
    params = {
        "q": query,
        "offset": (page - 1) * 20,
    }
    resp = requests.get(
        "https://search.brave.com/search",
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    anchors = soup.select("a.result-header, a.result__a")
    return [a.get("href") for a in anchors if a.get("href")]


def fetch_google(query: str, page: int) -> List[str]:
    """Google HTML results. May be rate-limited or show consent pages."""
    params = {
        "q": query,
        "start": (page - 1) * 10,
        "num": 10,
        "hl": "en",
    }
    resp = requests.get(
        "https://www.google.com/search",
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    anchors = soup.select("a")
    links: List[str] = []
    for a in anchors:
        href = a.get("href")
        if not href or not href.startswith("http"):
            continue
        if "google." in href and "url?" not in href:
            continue
        links.append(href)
    return links


def fetch_yahoo(query: str, page: int) -> List[str]:
    """Yahoo HTML results."""
    params = {
        "p": query,
        "b": (page - 1) * 10 + 1,
    }
    resp = requests.get(
        "https://search.yahoo.com/search",
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    anchors = soup.select("div#web h3.title a, div#web h3 a")
    return [a.get("href") for a in anchors if a.get("href")]


FETCHERS: Dict[str, Callable[[str, int], List[str]]] = {
    "duckduckgo": fetch_duckduckgo,
    "bing": fetch_bing,
    "edge": fetch_bing,  # Edge uses Bing results
    "brave": fetch_brave,
    "google": fetch_google,
    "yahoo": fetch_yahoo,
}


def collect_links(query: str, pages: int, engine: str) -> List[str]:
    """Collect links across pages for one engine or all engines, de-duplicated in order."""
    engines = list(FETCHERS) if engine == "all" else [engine]
    seen = set()
    ordered: List[str] = []
    for eng in engines:
        fetcher = FETCHERS[eng]
        for page in range(1, pages + 1):
            try:
                links = fetcher(query, page)
            except Exception as exc:  # noqa: BLE001 - user-facing script
                print(f"[{eng} page {page}] error: {exc}", file=sys.stderr)
                continue
            for link in links:
                if link in seen:
                    continue
                seen.add(link)
                ordered.append(link)
            time.sleep(1)
    return ordered


def write_links(path: Path, links: Iterable[str]) -> None:
    """Write links to a text file, one per line."""
    with path.open("w", encoding="utf-8") as f:
        for link in links:
            f.write(f"{link}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search-engine link collector")
    parser.add_argument("-q", "--query", help="Search query text")
    parser.add_argument(
        "-p", "--pages", type=int, default=None, help="Number of result pages (>=1)"
    )
    parser.add_argument(
        "-e",
        "--engine",
        choices=sorted((*FETCHERS.keys(), "all")),
        default=None,
        help="Search engine to use (or 'all' to combine)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional output path for links file (defaults to links_<engine>.txt)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        query = (args.query or input("Enter a keyword to search: ")).strip()
        pages: Optional[int] = args.pages
        if pages is None:
            pages = int(input("How many pages to fetch? "))
        engine = (args.engine or input(
            "Choose engine (duckduckgo|bing|edge|brave|google|yahoo|all) [all]: "
        ).strip().lower() or "all")
    except Exception:
        print("Invalid input. Please enter a keyword, engine, and number of pages.")
        return

    if not query:
        print("Query cannot be empty.")
        return
    if pages < 1:
        print("Page count must be at least 1.")
        return
    if engine not in FETCHERS and engine != "all":
        print(
            f"Unknown engine '{engine}'. Choose from: "
            f"{', '.join((*FETCHERS.keys(), 'all'))}"
        )
        return

    links = collect_links(query, pages, engine)
    output_path = Path(args.output) if args.output else Path(__file__).with_name(
        f"links_{engine}.txt"
    )
    write_links(output_path, links)

    print(f"Saved {len(links)} links to {output_path}")


if __name__ == "__main__":
    main()