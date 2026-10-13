"""Testy AI Digest — parsowanie z fixture'ów, filtr, dedupe, raport. Bez sieci."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_digest.filter import relevant, score_item  # noqa: E402
from ai_digest.report import render_html, render_md  # noqa: E402
from ai_digest.sources import Item, parse_arxiv, parse_hn, parse_rss  # noqa: E402
from ai_digest.state import Seen  # noqa: E402

HN_FIXTURE = """{"hits": [
  {"title": "Show HN: My local LLM setup", "url": "https://example.com/llm", "objectID": "1", "story_text": null},
  {"title": "A cookbook of bread recipes", "url": "https://example.com/bread", "objectID": "2", "story_text": null}
]}"""

ARXIV_FIXTURE = """<feed xmlns="http://www.w3.org/2005/Atom">
  <entry><title>Fine-tuning of transformer models
</title><id>http://arxiv.org/abs/2401.00001v1</id>
<summary>We study fine-tuning of LLMs.  </summary></entry>
  <entry><title>Quantum chemistry advances</title><id>http://arxiv.org/abs/2401.00002v1</id><summary>Chemistry.</summary></entry>
</feed>"""

RSS_FIXTURE = """<rss><channel>
<item><title>Nowy otwarty model językowy</title><link>https://example.com/model</link><description>Polski LLM</description></item>
</channel></rss>"""


class TestParsing(unittest.TestCase):
    def test_parse_hn(self):
        items = parse_hn(HN_FIXTURE)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].source, "Hacker News")
        # gdy hit ma własny URL — używamy go; fallback na discussion tylko bez URL-a
        self.assertEqual(items[1].url, "https://example.com/bread")

    def test_parse_arxiv_czyści_tytuły(self):
        items = parse_arxiv(ARXIV_FIXTURE)
        self.assertEqual(items[0].title, "Fine-tuning of transformer models")
        self.assertTrue(items[0].url.startswith("http://arxiv.org/abs/"))

    def test_parse_rss(self):
        items = parse_rss(RSS_FIXTURE, source_name="Test RSS")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].source, "Test RSS")


class TestFilter(unittest.TestCase):
    def test_llm_tytul_ma_trafienia(self):
        s = score_item(Item("Show HN: My local LLM setup", "u", "HN"))
        self.assertGreaterEqual(s.score, 1)

    def test_chleb_odpada(self):
        scored = relevant([Item("A cookbook of bread recipes", "u", "HN")], min_score=1)
        self.assertEqual(scored, [])

    def test_sortowanie_po_trafieniach(self):
        scored = relevant([
            Item("LLM agents", "u1", "HN"),
            Item("LLM RAG embeddings agents", "u2", "arXiv"),
        ])
        self.assertEqual(scored[0].item.url, "u2")


class TestSeen(unittest.TestCase):
    def test_dedupe(self):
        with tempfile_dir() as path:
            seen_file = os.path.join(path, "seen.json")
            seen = Seen(seen_file)
            self.assertTrue(seen.is_new("https://a"))
            seen.mark("https://a")
            seen2 = Seen(seen_file)  # reload
            self.assertFalse(seen2.is_new("https://a"))
            self.assertTrue(seen2.is_new("https://b"))


def tempfile_dir():
    import tempfile
    return tempfile.TemporaryDirectory()


class TestReport(unittest.TestCase):
    def test_html_i_md(self):
        scored = relevant([Item("LLM agents", "https://x", "HN")])
        html = render_html(scored, "2026-10-13")
        md = render_md(scored, "2026-10-13")
        self.assertIn("AI·DIGEST", html)
        self.assertIn("https://x", html)
        self.assertIn("[LLM agents](https://x)", md)


if __name__ == "__main__":
    unittest.main()
