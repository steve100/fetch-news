#!/usr/bin/env python3
"""
Top News Aggregator — HTML, Markdown, JSON, CSV (AI-first default)
------------------------------------------------------------------
Fetches headlines from multiple public RSS feeds (BBC, NYT, Google News, Reuters, AP where possible),
deduplicates by title/link, and prints up to N (default 20) one-line summaries with direct links.

- Output formats: markdown, html, json, csv
- AI/Tech-first ordering is enabled by default; disable with --no-ai-first
- When --output-file is used, the script writes to that path and does NOT print to stdout
  (unless --also-stdout is specified). Use --quiet to suppress stdout in all cases.
"""

import argparse
import datetime as dt
import json
import csv
import io
import re
import sys
from typing import Dict, Iterable, List, Optional, Tuple

import feedparser
from bs4 import BeautifulSoup
from html import unescape

# -----------------------------
# Config: Feeds
# -----------------------------

FEEDS_BASE: Dict[str, List[Tuple[str, str]]] = {
    "world": [
        ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
        ("NYT Home/Top", "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"),
        ("Google News (US Top Stories)", "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"),
        ("Reuters World (legacy)", "https://www.reuters.com/rss/worldNews"),
        ("Reuters Top (legacy)", "https://feeds.reuters.com/reuters/topNews"),
    ],
    "us": [
        ("BBC US & Canada", "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml"),
        ("NYT U.S.", "https://rss.nytimes.com/services/xml/rss/nyt/US.xml"),
        ("Google News (US Nation)", "https://news.google.com/rss/headlines/section/topic/NATION.en_us/US?hl=en-US&gl=US&ceid=US:en"),
        ("Reuters U.S. (legacy)", "https://feeds.reuters.com/Reuters/domesticNews"),
    ],
    "ai": [
        ("Google News (AI topic)", "https://news.google.com/rss/search?q=AI%20OR%20artificial%20intelligence&hl=en-US&gl=US&ceid=US:en"),
        ("NYT Technology", "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"),
        ("BBC Technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
        ("Reuters Technology (legacy)", "https://feeds.reuters.com/reuters/technologyNews"),
    ],
}

DEFAULT_ORDER = ["ai", "us", "world"]

def _display_name(section: str) -> str:
    mapping = {"ai": "AI", "us": "U.S.", "world": "World"}
    return mapping.get(section, section.title())

def make_title_from_sections(sections: List[str]) -> str:
    disp = ", ".join(_display_name(s) for s in sections)
    return f"Top News ({disp})"

# -----------------------------
# Helpers
# -----------------------------

PUNCT_RE = re.compile(r"[^\w\s]")
WHITESPACE_RE = re.compile(r"\s+")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

def strip_html(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(" ", strip=True)

def normalize_title(title: str) -> str:
    title = unescape(strip_html(title or "")).lower().strip()
    title = PUNCT_RE.sub(" ", title)
    title = WHITESPACE_RE.sub(" ", title)
    return title

def best_link(entry) -> Optional[str]:
    for key in ("link", "id", "guid"):
        val = getattr(entry, key, None) or entry.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    links = getattr(entry, "links", None) or entry.get("links")
    if isinstance(links, list) and links:
        for l in links:
            if isinstance(l, dict) and l.get("href"):
                return l["href"]
    return None

def summarize_entry(entry) -> str:
    text_fields = []
    for key in ("summary", "description", "content"):
        val = getattr(entry, key, None) or entry.get(key)
        if not val:
            continue
        if isinstance(val, list):
            text_fields.extend([c.get("value", "") for c in val if isinstance(c, dict)])
        elif isinstance(val, str):
            text_fields.append(val)

    if text_fields:
        raw = " ".join(text_fields)
        raw = strip_html(unescape(raw))
        parts = SENTENCE_SPLIT.split(raw)
        if parts:
            first = parts[0].strip()
            first = WHITESPACE_RE.sub(" ", first)
            if first:
                return first

    title = getattr(entry, "title", None) or entry.get("title") or ""
    title = strip_html(unescape(title))
    title = WHITESPACE_RE.sub(" ", title).strip()
    return title[:300]

def parse_feed(section: str, source: str, url: str):
    fp = feedparser.parse(url)
    items = []
    for e in fp.entries or []:
        title = getattr(e, "title", None) or e.get("title") or ""
        link = best_link(e)
        summary = summarize_entry(e)
        published_dt = None
        if getattr(e, "published_parsed", None):
            try:
                published_dt = dt.datetime(*e.published_parsed[:6], tzinfo=dt.timezone.utc)
            except Exception:
                published_dt = None
        elif getattr(e, "updated_parsed", None):
            try:
                published_dt = dt.datetime(*e.updated_parsed[:6], tzinfo=dt.timezone.utc)
            except Exception:
                published_dt = None
        items.append((section, source, title, link, summary, published_dt))
    return items

def merge_and_dedupe(feeds: Dict[str, List[Tuple[str, str]]],
                     include: Iterable[str],
                     limit: int = 20) -> List[Tuple[str, str, str, str, str, Optional[dt.datetime]]]:
    seen: set = set()
    merged: List[Tuple[str, str, str, str, str, Optional[dt.datetime]]] = []

    for section in include:
        for source, url in feeds.get(section, []):
            try:
                entries = parse_feed(section, source, url)
            except Exception:
                continue
            for sec, src, title, link, summary, ts in entries:
                if not (title or link):
                    continue
                key = (normalize_title(title), (link or "").strip())
                if key in seen:
                    continue
                seen.add(key)
                merged.append((sec, src, title, link, summary, ts))

    merged.sort(key=lambda x: (x[5] is None, x[5] and -x[5].timestamp(), x[1]))
    return merged[:limit]

# -----------------------------
# Renderers
# -----------------------------

def render_markdown(items):
    lines = []
    for sec, src, title, link, summary, ts in items:
        link_text = link or "(no link)"
        one_liner = summary if summary else (title or "").strip()
        one_liner = re.sub(r"\s+", " ", (one_liner or "")).strip()
        if not one_liner:
            continue
        lines.append(f"- {one_liner}  \n  {link_text}")
    return "\n".join(lines) + ("\n" if lines else "")

def render_html(items, title="Top News"):
    parts = [
        "<!doctype html>",
        "<html lang='en'>",
        "<head>",
        "  <meta charset='utf-8'/>",
        f"  <title>{title}</title>",
        "  <meta name='viewport' content='width=device-width, initial-scale=1'/>",
        "  <style>",
        "    body{font:16px/1.5 system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin:2rem; color:#111}",
        "    h1{font-size:1.6rem; margin:0 0 1rem}",
        "    ul{list-style:disc; padding-left:1.2rem}",
        "    li{margin:0.5rem 0}",
        "    .src{opacity:0.7; font-size:0.9rem; margin-left:0.25rem}",
        "    a{word-break:break-word; text-decoration:none}",
        "    .newslink{font-size:0.8rem; color:#0645AD; display:block; margin-top:0.2rem}",
        "    .newslink:hover{color:#0b0080; text-decoration:underline}",
        "    a:hover{text-decoration:underline}",
        "  </style>",
        "</head>",
        "<body>",
        f"  <h1>{title}</h1>",
        "  <ul>"
    ]
    for sec, src, _title, link, summary, ts in items:
        safe_summary = (summary or _title or "").replace("<", "&lt;").replace(">", "&gt;")
        href = (link or "").replace('"', "%22")
        parts.append("    <li>")
        parts.append(f"      <p>{safe_summary} <span class='src'>({src})</span></p>")
        if href:
            parts.append(f'      <a class="newslink" href="{href}" target="_blank" rel="noopener noreferrer">{href}</a>')
        parts.append("    </li>")
    parts.extend([
        "  </ul>",
        "</body>",
        "</html>"
    ])
    return "\n".join(parts)

def _iso(ts: Optional[dt.datetime]) -> Optional[str]:
    if not ts:
        return None
    try:
        return ts.astimezone(dt.timezone.utc).isoformat()
    except Exception:
        return None

def render_json(items):
    data = []
    for sec, src, title, link, summary, ts in items:
        data.append({
            "section": sec,
            "source": src,
            "title": title,
            "link": link,
            "summary": summary,
            "published": _iso(ts),
        })
    return json.dumps(data, ensure_ascii=False, indent=2)

def render_csv(items):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["section", "source", "title", "link", "summary", "published"])
    for sec, src, title, link, summary, ts in items:
        writer.writerow([sec, src, title, link, summary, _iso(ts) or ""])
    return output.getvalue()

# -----------------------------
# Helpers: paths
# -----------------------------

def _derive_base_path(output_file: str) -> str:
    """Given an output_file (optional), return a base path without extension.
    If not provided, default to 'top_news' in cwd.
    """
    if output_file:
        p = __import__('pathlib').Path(output_file)
        stem = p.stem
        parent = p.parent if str(p.parent) != '' else __import__('pathlib').Path('.')
        return str(parent / stem)
    else:
        return 'top_news'

# -----------------------------
# CLI
# -----------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description="Top News Aggregator (BBC/NYT/Google/Reuters/AP)")
    parser.add_argument("--max", type=int, default=20, help="Maximum number of stories to output (<= 50)")
    parser.add_argument("--include-world", action="store_true", help="Include World feeds")
    parser.add_argument("--include-us", action="store_true", help="Include U.S. feeds")
    parser.add_argument("--include-ai", action="store_true", help="Include AI/Tech feeds")
    parser.add_argument("--no-ai-first", action="store_true", help="Disable AI/Tech-first ordering (default is AI-first)")
    parser.add_argument("--format", choices=["markdown", "html", "json", "csv"], default="markdown", help="Output format")
    parser.add_argument("--all-formats", action="store_true", help="Write HTML, JSON, and CSV files in one run")
    parser.add_argument("--output-file", type=str, default="", help="Optional path to save output (md/html/json/csv)")
    parser.add_argument("--markdown-file", type=str, default="", help="(Deprecated) Save Markdown output to this path")
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout output")
    parser.add_argument("--also-stdout", action="store_true", help="Print to stdout even when --output-file is used")
    args = parser.parse_args(argv)

    limit = max(1, min(args.max, 50))

    include_sections = [sec for sec, flag in zip(
        ["world", "us", "ai"],
        [args.include_world, args.include_us, args.include_ai]
    ) if flag]
    if not include_sections:
        include_sections = DEFAULT_ORDER[:]

    if args.markdown_file and not args.output_file:
        args.output_file = args.markdown_file
        args.format = "markdown"

    title = make_title_from_sections(include_sections)
    items = merge_and_dedupe(FEEDS_BASE, include_sections, limit=limit)

    if not args.no_ai_first:
        def section_weight(section: str) -> int:
            return 0 if section == "ai" else 1
        items.sort(key=lambda x: (section_weight(x[0]), x[5] is None, x[5] and -x[5].timestamp(), x[1]))

    if args.all_formats:
        # Build all outputs
        md_out = render_markdown(items)
        html_out = render_html(items, title=title)
        json_out = render_json(items)
        csv_out = render_csv(items)

        base = _derive_base_path(args.output_file)
        targets = [
            (md_out, base + ".md"),
            (html_out, base + ".html"),
            (json_out, base + ".json"),
            (csv_out, base + ".csv"),
        ]
        for content, path in targets:
            try:
                from pathlib import Path as _P
                out_path = _P(path)
                if out_path.parent and not out_path.parent.exists():
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "w", encoding="utf-8", newline="") as f:
                    f.write(content)
                print(f"# Wrote: {out_path.resolve()}", file=sys.stderr)
            except Exception as e:
                print(f"# Warn: failed to write output file: {e}", file=sys.stderr)

        # stdout behavior for all-formats: default no print; print markdown if explicitly requested
        if args.also_stdout and not args.quiet:
            print(md_out)
    else:
        # Single-format path (existing behavior)
        if args.format == "markdown":
            out = render_markdown(items)
        elif args.format == "html":
            out = render_html(items, title=title)
        elif args.format == "json":
            out = render_json(items)
        else:  # csv
            out = render_csv(items)

        if args.output_file:
            try:
                from pathlib import Path as _P
                out_path = _P(args.output_file)
                if out_path.parent and not out_path.parent.exists():
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "w", encoding="utf-8", newline="") as f:
                    f.write(out)
                print(f"# Wrote: {out_path.resolve()}", file=sys.stderr)
            except Exception as e:
                print(f"# Warn: failed to write output file: {e}", file=sys.stderr)

        should_print = True
        if args.quiet:
            should_print = False
        elif args.output_file and not args.also_stdout:
            should_print = False
        if should_print:
            print(out)
if __name__ == "__main__":
    main()
