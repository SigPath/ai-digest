"""Raporty: HTML (do Pages) i Markdown (do notatek/Telegrama)."""
import html
from datetime import datetime, timezone
from typing import List

from .filter import ScoredItem


def render_html(scored: List[ScoredItem], digest_date: str) -> str:
    items_html = []
    for s in scored:
        it = s.item
        badges = "".join(f"<span class='tag'>{html.escape(m)}</span>" for m in s.matched[:4])
        summary = f"<p class='sum'>{html.escape(' '.join(it.summary.split())[:240])}…</p>" if it.summary else ""
        items_html.append(
            f"<li><a href='{html.escape(it.url)}'>{html.escape(it.title)}</a>"
            f"<div class='meta'>{html.escape(it.source)} · trafienia: {s.score} {badges}</div>{summary}</li>"
        )

    return f"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Digest — {html.escape(digest_date)}</title>
<style>
:root {{ color-scheme: dark; }}
body {{ background:#101418; color:#e8ebef; font-family: system-ui, sans-serif; margin:0; padding:40px 20px; }}
main {{ max-width: 820px; margin:0 auto; }}
h1 {{ font-size:26px; }} h1 span {{ color:#ffb000; }}
.meta {{ color:#9aa4b0; font-size:13px; font-family:ui-monospace,monospace; margin:6px 0 26px; }}
ol {{ padding-left: 0; list-style: none; }}
li {{ padding: 14px 0; border-bottom: 1px solid #2a333e; }}
li a {{ color:#e8ebef; font-weight:600; text-decoration:none; font-size:16px; }}
li a:hover {{ color:#ffb000; }}
.meta {{ font-size:12px; margin:4px 0; }}
.sum {{ color:#9aa4b0; font-size:13.5px; margin:6px 0 0; }}
.tag {{ display:inline-block; font-family:ui-monospace,monospace; font-size:10px; text-transform:uppercase;
      border:1px solid #2a333e; color:#9aa4b0; padding:1px 7px; margin-left:4px; }}
.foot {{ color:#9aa4b0; font-size:12px; margin-top:30px; }}
.foot a {{ color:#ffb000; }}
</style></head>
<body><main>
<h1><span>AI·DIGEST</span> — przegląd świata AI</h1>
<p class="meta">{html.escape(digest_date)} · {len(scored)} pozycji · źródła: Hacker News + arXiv · filtr słów kluczowych</p>
<ol>{''.join(items_html)}</ol>
<p class="foot">Codziennie generowane przez <a href="https://github.com/SigPath/ai-digest">AI Digest</a> · Marcin Burda · <a href="https://burda.eu.org">burda.eu.org</a></p>
</main></body></html>"""


def render_md(scored: List[ScoredItem], digest_date: str) -> str:
    lines = [f"# AI Digest — {digest_date}", ""]
    for s in scored:
        lines.append(f"- [{s.item.title}]({s.item.url}) — *{s.item.source}*, trafienia: {s.score}")
    return "\n".join(lines) + "\n"


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
