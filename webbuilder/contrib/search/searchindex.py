"""webbuilder.contrib.search.searchindex — Search index (contrib)."""
from __future__ import annotations
from typing import Dict, Any, List


class SearchIndex:
    """Inverted index for full-text search."""

    def __init__(self):
        self._index: Dict[str, List[str]] = {}
        self._docs: Dict[str, str] = {}

    def add(self, doc_id: str, content: str) -> None:
        """Add or update a document in the index."""
        if doc_id in self._docs:
            old = self._docs[doc_id]
            for word in set(old.split()):
                self._index.get(word, [])
                if word in self._index and doc_id in self._index[word]:
                    self._index[word].remove(doc_id)

        self._docs[doc_id] = content
        for word in set(content.lower().split()):
            self._index.setdefault(word, []).append(doc_id)

    def search(self, query: str) -> List[str]:
        """Search the index. Returns list of doc_ids."""
        words = query.lower().split()
        results: List[str] = []
        for word in words:
            if word in self._index:
                results.extend(self._index[word])
        return list(set(results))
