"""
Library indexing and retrieval for the Librarian agent.

Provides:
  - get_index()          — load or rebuild the page index from notion_exports/
  - search_pages()       — keyword-score pages against a query
  - read_page_content()  — read a page's full Markdown from disk
  - build_librarian_context() — full pipeline: index summary + retrieved pages
"""
import json
import re
from pathlib import Path

from .config import config

# ── Constants ──────────────────────────────────────────────────────────────────

_NOTION_ID_RE = re.compile(r'\s+[0-9a-f]{32}$')

_STOP_WORDS = {
    "a", "an", "the", "is", "it", "in", "of", "and", "or", "to", "for",
    "what", "how", "why", "does", "do", "did", "can", "will", "would",
    "should", "tell", "me", "about", "page", "with", "this", "that",
    "are", "was", "were", "has", "have", "its", "on", "at", "by", "from",
    "which", "we", "our", "i", "you", "your",
}

MAX_PAGES_RETRIEVED = 2
MAX_CHARS_PER_PAGE = 4000


# ── Index build ────────────────────────────────────────────────────────────────

def _clean_title(stem: str) -> str:
    return _NOTION_ID_RE.sub('', stem).strip()


def _parse_md_meta(text: str) -> dict:
    meta = {}
    for line in text.splitlines()[1:40]:
        if line.startswith("## ") or line.startswith("---"):
            break
        if ": " in line and not line.startswith("#"):
            k, _, v = line.partition(": ")
            meta[k.strip()] = v.strip()
    return meta


def _scan_exports(exports_dir: Path) -> list:
    items = []
    for md_file in sorted(exports_dir.rglob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()

            title = _clean_title(md_file.stem)
            for line in lines[:5]:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            meta = _parse_md_meta(text)
            tags = [t.strip() for t in meta.get("Tags", "").split(",") if t.strip()]

            items.append({
                "title": title,
                "file": md_file.name,
                "rel_path": str(md_file.relative_to(exports_dir.parent.parent)),
                "section": meta.get("Section", ""),
                "priority": meta.get("Priority", ""),
                "page_type": meta.get("Page type", ""),
                "local_agent_use": meta.get("Local agent use", ""),
                "tags": tags,
            })
        except Exception:
            pass
    return items


def get_index(exports_dir: Path | None = None, index_path: Path | None = None) -> list:
    """Return the library index, rebuilding from disk if stale."""
    exports_dir = exports_dir or (config.LIBRARY_DIR / "notion_exports")
    index_path = index_path or (config.LIBRARY_DIR / "index.json")

    md_files = list(exports_dir.rglob("*.md"))
    if not md_files:
        return []

    newest_export = max(f.stat().st_mtime for f in md_files)
    if index_path.exists():
        if index_path.stat().st_mtime >= newest_export:
            try:
                data = json.loads(index_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return data
                if isinstance(data, dict) and "items" in data:
                    return data["items"]
            except Exception:
                pass

    items = _scan_exports(exports_dir)
    try:
        index_path.write_text(
            json.dumps({"built_from": "notion_exports_scan", "items": items}, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass
    return items


# ── Retrieval ──────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> set:
    words = re.sub(r'[^a-z0-9 ]', ' ', text.lower()).split()
    return {w for w in words if w not in _STOP_WORDS and len(w) > 1}


def _score_page(page: dict, query_words: set) -> int:
    title_words = _tokenize(page.get("title", ""))
    tag_words = _tokenize(" ".join(page.get("tags", [])))
    use_words = _tokenize(page.get("local_agent_use", ""))
    section_words = _tokenize(page.get("section", ""))

    return (
        len(query_words & title_words) * 3
        + len(query_words & tag_words) * 2
        + len(query_words & use_words)
        + len(query_words & section_words)
    )


def search_pages(query: str, index: list, max_pages: int = MAX_PAGES_RETRIEVED) -> list:
    """Return the top-scoring pages for a query, ordered by relevance score."""
    query_words = _tokenize(query)
    if not query_words:
        return []
    scored = [(p, _score_page(p, query_words)) for p in index]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [p for p, score in scored if score > 0][:max_pages]


def read_page_content(rel_path: str, base_dir: Path | None = None) -> str:
    """Read a page's Markdown content from disk, capped at MAX_CHARS_PER_PAGE."""
    base_dir = base_dir or config.LIBRARY_DIR.parent
    full_path = base_dir / rel_path
    if not full_path.exists():
        return ""
    text = full_path.read_text(encoding="utf-8", errors="replace")
    if len(text) > MAX_CHARS_PER_PAGE:
        text = text[:MAX_CHARS_PER_PAGE] + "\n\n[...content truncated for context length...]"
    return text


# ── Librarian context builder ──────────────────────────────────────────────────

def build_librarian_context(query: str) -> str:
    """
    Build the auto-injected context for a Librarian query.

    Always includes:
      - Compact index of all available pages (title, section, tags)

    Plus, for queries that match pages:
      - Full content of up to MAX_PAGES_RETRIEVED matching pages
    """
    exports_dir = config.LIBRARY_DIR / "notion_exports"
    index_path = config.LIBRARY_DIR / "index.json"
    index = get_index(exports_dir, index_path)

    if not index:
        return ""

    # Compact index summary
    index_lines = [f"## Library index ({len(index)} pages available)\n"]
    for item in index:
        tags_str = ", ".join(item.get("tags", [])) or "—"
        section = item.get("section", "—")
        index_lines.append(f"- **{item['title']}** | {section} | tags: {tags_str}")
    index_summary = "\n".join(index_lines)

    # Retrieve matching pages
    matches = search_pages(query, index)
    if not matches:
        return index_summary

    parts = [index_summary, f"\n## Retrieved pages ({len(matches)} matched your query)\n"]
    base_dir = config.LIBRARY_DIR.parent
    for page in matches:
        content = read_page_content(page["rel_path"], base_dir)
        if content:
            parts.append(f"=== {page['title']} ===\nFile: {page['rel_path']}\n\n{content}")

    return "\n\n".join(parts)
