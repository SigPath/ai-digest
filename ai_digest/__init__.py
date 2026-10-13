"""AI Digest — dzienny przegląd świata AI: HN + arXiv → filtr → raport (opcjonalnie LLM streszcza)."""
from .sources import Item, fetch_hn, fetch_arxiv, fetch_rss, parse_hn, parse_arxiv, parse_rss
from .filter import relevant, score_item
from .state import Seen
from .report import render_html, render_md

__version__ = "1.0.0"
__all__ = [
    "Item", "fetch_hn", "fetch_arxiv", "fetch_rss", "parse_hn", "parse_arxiv", "parse_rss",
    "relevant", "score_item", "Seen", "render_html", "render_md", "__version__",
]
