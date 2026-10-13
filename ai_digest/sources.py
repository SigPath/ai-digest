"""Źródła: Hacker News (JSON API), arXiv (Atom), ogólny RSS. Fetch wstrzykiwalny → testy bez sieci."""
import json
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Callable, List

Fetch = Callable[[str], str]


@dataclass
class Item:
    title: str
    url: str
    source: str
    summary: str = ""

    @property
    def key(self) -> str:
        return self.url or self.title


def http_get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "ai-digest/1.0 (portfolio SigPath)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_hn(body: str, limit: int = 15) -> List[Item]:
    data = json.loads(body)
    items = []
    for hit in data.get("hits", [])[:limit]:
        title = (hit.get("title") or "").strip()
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
        if title:
            items.append(Item(title=title, url=url, source="Hacker News",
                              summary=(hit.get("story_text") or "")[:300]))
    return items


def fetch_hn(fetch: Fetch = http_get, limit: int = 15) -> List[Item]:
    return parse_hn(fetch("https://hn.algolia.com/api/v1/search?tags=front_page"), limit=limit)


def parse_arxiv(body: str, limit: int = 15) -> List[Item]:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(body)
    items = []
    for entry in root.findall("a:entry", ns)[:limit]:
        title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip().replace("\n", " ")
        url = (entry.findtext("a:id", default="", namespaces=ns) or "").strip()
        summary = (entry.findtext("a:summary", default="", namespaces=ns) or "").strip().replace("\n", " ")[:400]
        if title:
            items.append(Item(title=title, url=url, source="arXiv", summary=summary))
    return items


def fetch_arxiv(fetch: Fetch = http_get, limit: int = 15) -> List[Item]:
    url = ("https://export.arxiv.org/api/query?search_query="
           "all:%22large+language+model%22+OR+all:%22LLM%22&sortBy=submittedDate&max_results=15")
    return parse_arxiv(fetch(url), limit=limit)


def parse_rss(body: str, source_name: str = "RSS", limit: int = 15) -> List[Item]:
    root = ET.fromstring(body)
    items = []
    for entry in list(root.iter("item"))[:limit]:
        title = (entry.findtext("title") or "").strip()
        link = (entry.findtext("link") or "").strip()
        desc = (entry.findtext("description") or "").strip()[:300]
        if title:
            items.append(Item(title=title, url=link, source=source_name, summary=desc))
    return items


def fetch_rss(url: str, source_name: str, fetch: Fetch = http_get, limit: int = 15) -> List[Item]:
    return parse_rss(fetch(url), source_name=source_name, limit=limit)
