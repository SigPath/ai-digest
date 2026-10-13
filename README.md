# AI Digest

**Dzienny przegląd świata AI po polsku**: Hacker News + arXiv → filtr słów kluczowych →
jeden raport HTML/Markdown. Publikowany automatycznie codziennie przez GitHub Actions.

→ **Dzienny raport (live):** https://sigpath.github.io/ai-digest/

## Jak działa

1. **Źródła** (bez kluczy): Hacker News front page (JSON API) + arXiv (Atom, „large language model"),
2. **Filtr relewancji**: punkty za słowa kluczowe PL/EN (LLM, RAG, embedding, fine-tuning…),
   zero trafień = odpada,
3. **Deduplikacja**: stan `seen.json` (hash URL) — nowe pozycje pierwsze,
4. **Raport**: samodzielny HTML + Markdown; awaria jednego źródła nie zabija digestu.

Czysty Python 3.9+, zero zależności. Fetch jest wstrzykiwalny — testy chodzą na fixture'ach, bez sieci.

## Szybki start

```bash
python3 tests/test_digest.py            # 8 testów
python3 -m ai_digest run                # raport: docs/index.html + out/digest.md
python3 -m ai_digest run --min-score 2  # tylko mocno on-topikowe
```

## Automatyczny codzienny raport

Workflow `.github/workflows/digest.yml` (cron 05:30 UTC) uruchamia digest i publikuje
`docs/index.html` na GitHub Pages. Historia stanu trwa w repo (`data/seen.json` commitowany
przez action), więc „nowe" naprawdę znaczy nowe.

## Uczciwe ograniczenia

- streszczenia LLM są zaplanowane (Ollama), na razie filtr jest czysto słownikowy,
- OLX-owa lekcja z EV Radar zastosowana: brak źródeł wymagających omijania zabezpieczeń.

## Licencja

MIT
