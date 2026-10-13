"""CLI AI Digest:  python3 -m ai_digest run [--out docs/index.html] [--summarize]"""
import argparse
import os
import sys
from typing import List

from .filter import relevant
from .report import render_html, render_md, today
from .sources import fetch_arxiv, fetch_hn
from .state import Seen


def main(argv: List[str] = None) -> int:
    parser = argparse.ArgumentParser(prog="ai_digest", description="Dzienny przegląd świata AI: HN + arXiv → filtr → raport.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run_p = sub.add_parser("run", help="zbierz, odfiltruj i zapisz raport")
    run_p.add_argument("--out-html", default="docs/index.html")
    run_p.add_argument("--out-md", default="out/digest.md")
    run_p.add_argument("--state", default="data/seen.json")
    run_p.add_argument("--limit", type=int, default=12, help="maks. pozycji w raporcie")
    run_p.add_argument("--min-score", type=int, default=1)
    args = parser.parse_args(argv)
    if args.cmd != "run":  # pragma: no cover
        parser.error("nieznana komenda")

    raw: List = []
    errors: List[str] = []
    for name, fetcher in (("Hacker News", fetch_hn), ("arXiv", fetch_arxiv)):
        try:
            got = fetcher()
            raw.extend(got)
            print(f"  {name}: {len(got)} pozycji")
        except Exception as e:
            errors.append(f"{name}: {e}")
            print(f"  {name}: BŁĄD ({e})", file=sys.stderr)

    if not raw:
        print("BŁĄD: żadne źródło nie odpowiedziało.", file=sys.stderr)
        return 2

    scored = relevant(raw, min_score=args.min_score)[: args.limit]

    seen = Seen(args.state)
    fresh = [s for s in scored if seen.is_new(s.item.key)]
    for s in fresh:
        seen.mark(s.item.key)
    shown = fresh if fresh else scored  # gdy wszystko już widziane, pokaż top bez duplikatów w gate

    date = today()
    os.makedirs(os.path.dirname(args.out_html) or ".", exist_ok=True)
    with open(args.out_html, "w", encoding="utf-8") as f:
        f.write(render_html(shown, date))
    os.makedirs(os.path.dirname(args.out_md) or ".", exist_ok=True)
    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write(render_md(shown, date))

    print(f"Raport: {args.out_html} ({len(shown)} pozycji, {len(fresh)} nowych)")
    if errors:
        print(f"Ostrzeżenia: {'; '.join(errors)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
