"""Filtr relewancji: punkty za słowa kluczowe AI (PL/EN). Zero trafień = odpada."""
import re
from dataclasses import dataclass
from typing import List

KEYWORDS = [
    r"\bllm\b", r"\blarge language model", r"model(jezykowy| językowy)",
    r"\bai\b", r"\bartificial intelligence\b", r"sztuczn\w+ inteligencj\w+",
    r"\bagent", r"\brag\b", r"embedding", r"\bfine[- ]?tun", r"\bonnx\b",
    r"\bgpu\b", r"inferencj", r"\btransformer", r"\bollama\b", r"\bllama\b",
    r"\bmistral\b", r"\bgpt[- ]?\d", r"\bclaude\b", r"\bgemini\b", r"whisper",
    r"\bdiffusion\b", r"\bopen[- ]?source", r"otwart\w+ model",
]


@dataclass
class ScoredItem:
    item: object
    score: int
    matched: List[str]


def score_item(item) -> ScoredItem:
    text = f"{item.title} {item.summary}".lower()
    matched = []
    for pattern in KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            matched.append(pattern)
    return ScoredItem(item=item, score=len(matched), matched=matched)


def relevant(items: List, min_score: int = 1) -> List[ScoredItem]:
    scored = [score_item(i) for i in items]
    scored = [s for s in scored if s.score >= min_score]
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored
