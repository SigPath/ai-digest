"""Stan „już widziane": deduplikacja między dniami (hash URL-a)."""
import hashlib
import json
import os
from typing import Optional, Set


def _hash(key: str) -> str:
    return hashlib.sha1(key.encode()).hexdigest()[:16]


class Seen:
    def __init__(self, path: Optional[str] = "data/seen.json"):
        self.path = path
        self.seen: Set[str] = set()
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.seen = set(json.load(f))

    def is_new(self, key: str) -> bool:
        return _hash(key) not in self.seen

    def mark(self, key: str) -> None:
        self.seen.add(_hash(key))
        self._save()

    def _save(self) -> None:
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(sorted(self.seen), f)
