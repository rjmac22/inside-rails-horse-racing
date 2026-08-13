#!/usr/bin/env python3
"""Probe the public BHA Industry Statistics (Dashing) application without credentials.

The BHA website embeds https://dashing.horseracing.software/ as its Industry Statistics
application. Search-engine extraction exposes only the beta application shell, so this
bounded probe inspects the public HTML and JavaScript assets to identify dashboard labels
and public data routes. It deliberately sends no Authorization header and performs no
bulk data acquisition.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


PROJECT_ROOT = Path("/home/rob/Documents/inside-rails-horse-racing")
CACHE_DIR = (
    PROJECT_ROOT
    / "data"
    / "cache"
    / "bha_official_source_feasibility"
    / "dashing_public_surface_probe"
)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

APP_URL = "https://dashing.horseracing.software/"
HTML_CACHE = CACHE_DIR / "index.html"
INVENTORY_CACHE = CACHE_DIR / "inventory.json"

USER_AGENT = "Mozilla/5.0"
MAX_SCRIPT_BYTES = 8_000_000
MAX_SCRIPTS = 30


def fetch_public(url: str) -> tuple[int | None, str | None, bytes, str | None]:
    """Fetch one public resource without credentials and preserve failure evidence."""
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/javascript,text/javascript,*/*;q=0.8",
        },
    )

    try:
        with urlopen(request, timeout=30) as response:
            body = response.read(MAX_SCRIPT_BYTES + 1)
            return (
                response.status,
                response.headers.get("Content-Type"),
                body,
                None,
            )
    except HTTPError as error:
        body = error.read(MAX_SCRIPT_BYTES + 1)
        return error.code, error.headers.get("Content-Type"), body, f"HTTPError {error.code}"
    except URLError as error:
        return None, None, b"", f"URLError {error.reason!r}"


def stable_cache_name(url: str, sequence: int) -> str:
    """Create a local cache filename without assuming remote asset naming is unique."""
    parsed = urlparse(url)
    leaf = Path(parsed.path).name or f"asset_{sequence}.js"
    leaf = re.sub(r"[^A-Za-z0-9._-]+", "_", leaf)
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    return f"{sequence:02d}_{digest}_{leaf}"


# ---------------------------------------------------------------------------
# 1. Fetch the public application shell.
# ---------------------------------------------------------------------------
#
# This is deliberately one HTML request. No BHA credential is read or sent.
# The raw response is cached before we interpret it.

status, content_type, html_bytes, html_error = fetch_public(APP_URL)

HTML_CACHE.write_bytes(html_bytes)

print("BHA INDUSTRY STATISTICS / DASHING — PUBLIC SURFACE PROBE")
print("========================================================")
print("Application:", APP_URL)
print("HTTP status:", status)
print("Content-Type:", content_type)
print("Bytes:", len(html_bytes))
print("SHA-256:", hashlib.sha256(html_bytes).hexdigest() if html_bytes else None)
print("Transport error:", html_error)
print("Authorization sent: NO")

if status != 200 or not html_bytes:
    raise SystemExit("Unable to retrieve the public Dashing application shell.")

html_text = html_bytes.decode("utf-8", errors="replace")

# ---------------------------------------------------------------------------
# 2. Discover public JavaScript bundles referenced by the shell.
# ---------------------------------------------------------------------------
#
# We only follow script src attributes from this first-party page. Inline
# JavaScript is also inspected locally because it may contain route/config data.

script_srcs = re.findall(
    r"<script\b[^>]*\bsrc\s*=\s*['\"]([^'\"]+)['\"]",
    html_text,
    flags=re.IGNORECASE,
)

script_urls: list[str] = []
for src in script_srcs:
    absolute = urljoin(APP_URL, unescape(src).strip())
    if absolute not in script_urls:
        script_urls.append(absolute)

print("\nSCRIPT BUNDLES")
print("==============")
print("Discovered script src values:", len(script_urls))
for url in script_urls[:MAX_SCRIPTS]:
    print(" ", url)

if len(script_urls) > MAX_SCRIPTS:
    print(f"  ... bounded at first {MAX_SCRIPTS} scripts")

# ---------------------------------------------------------------------------
# 3. Fetch a bounded set of public script bundles and cache every response.
# ---------------------------------------------------------------------------

assets: list[dict[str, object]] = []
texts_to_search: list[tuple[str, str]] = [("index.html", html_text)]

for sequence, script_url in enumerate(script_urls[:MAX_SCRIPTS], start=1):
    script_status, script_type, body, script_error = fetch_public(script_url)

    cache_name = stable_cache_name(script_url, sequence)
    cache_path = CACHE_DIR / cache_name
    cache_path.write_bytes(body)

    truncated = len(body) > MAX_SCRIPT_BYTES
    if truncated:
        body = body[:MAX_SCRIPT_BYTES]

    asset = {
        "url": script_url,
        "status": script_status,
        "content_type": script_type,
        "bytes_received": cache_path.stat().st_size,
        "sha256": hashlib.sha256(cache_path.read_bytes()).hexdigest() if cache_path.exists() else None,
        "transport_error": script_error,
        "analysis_truncated_at_bytes": MAX_SCRIPT_BYTES if truncated else None,
        "cache_file": str(cache_path),
    }
    assets.append(asset)

    if body:
        texts_to_search.append((cache_name, body.decode("utf-8", errors="replace")))

# ---------------------------------------------------------------------------
# 4. Extract candidate URLs/routes from the public code.
# ---------------------------------------------------------------------------
#
# These are observations of strings in the application assets. A route name is
# not treated as a proven live API until the application or a later tiny request
# demonstrates it.

URL_PATTERN = re.compile(r"https?://[^\s'\"<>\\)]+", flags=re.IGNORECASE)
ROUTE_PATTERN = re.compile(
    r"['\"]((?:/|\.\./|\./)(?:api|bha|data|stats|statistics|dashboard|report|racing)[^'\"\s]{0,180})['\"]",
    flags=re.IGNORECASE,
)

candidate_urls: set[str] = set()
candidate_routes: set[str] = set()

for _, text in texts_to_search:
    candidate_urls.update(URL_PATTERN.findall(text))
    candidate_routes.update(match.group(1) for match in ROUTE_PATTERN.finditer(text))

# ---------------------------------------------------------------------------
# 5. Recover human-facing dashboard/statistics labels.
# ---------------------------------------------------------------------------
#
# Minified bundles contain a great deal of incidental text. We therefore print
# bounded contexts only around terms that describe likely racing-statistics
# measures or dimensions, rather than dumping entire JavaScript files.

TERMS = [
    "fixture",
    "race",
    "runner",
    "horse",
    "field size",
    "prize",
    "declaration",
    "entry",
    "non-runner",
    "abandon",
    "flat",
    "jump",
    "all weather",
    "awt",
    "punctual",
    "off time",
    "compet",
    "handicap",
    "population",
    "trainer",
    "jockey",
    "owner",
]

contexts: list[dict[str, str]] = []
seen_contexts: set[str] = set()

for source_name, text in texts_to_search:
    lower = text.lower()
    for term in TERMS:
        start_at = 0
        matches_for_term = 0
        while matches_for_term < 4:
            position = lower.find(term.lower(), start_at)
            if position < 0:
                break

            start = max(0, position - 180)
            end = min(len(text), position + len(term) + 320)
            context = re.sub(r"\s+", " ", text[start:end]).strip()
            signature = context.lower()

            if signature not in seen_contexts:
                seen_contexts.add(signature)
                contexts.append(
                    {
                        "source": source_name,
                        "term": term,
                        "context": context,
                    }
                )

            matches_for_term += 1
            start_at = position + len(term)

# ---------------------------------------------------------------------------
# 6. Persist a compact inventory before printing bounded findings.
# ---------------------------------------------------------------------------

inventory = {
    "provider": "British Horseracing Authority",
    "source_family": "Industry Statistics / Dashing",
    "application_url": APP_URL,
    "analysed_at_utc": datetime.now(timezone.utc).isoformat(),
    "authorization_sent": False,
    "html": {
        "status": status,
        "content_type": content_type,
        "bytes": len(html_bytes),
        "sha256": hashlib.sha256(html_bytes).hexdigest(),
        "cache_file": str(HTML_CACHE),
    },
    "script_urls": script_urls,
    "assets": assets,
    "candidate_urls": sorted(candidate_urls),
    "candidate_routes": sorted(candidate_routes),
    "contexts": contexts,
}

INVENTORY_CACHE.write_text(
    json.dumps(inventory, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("\nFETCHED ASSETS")
print("==============")
for asset in assets:
    print(
        f"status={asset['status']} bytes={asset['bytes_received']} "
        f"type={asset['content_type']} url={asset['url']}"
    )

print("\nCANDIDATE ABSOLUTE URLS")
print("=======================")
for value in sorted(candidate_urls)[:80]:
    print(" ", value)

print("\nCANDIDATE DATA/API ROUTES")
print("=========================")
for value in sorted(candidate_routes)[:120]:
    print(" ", value)

print("\nBOUNDED STATISTICS-LABEL CONTEXTS")
print("=================================")
for item in contexts[:100]:
    print(f"\n[{item['source']}] term={item['term']!r}")
    print(item["context"][:1200])

print("\nPROVENANCE")
print("==========")
print("Cache directory:", CACHE_DIR)
print("Inventory:", INVENTORY_CACHE)
print("Application HTML requests: 1")
print("JavaScript asset requests:", len(assets))
print("Authorization read: NO")
print("Authorization sent: NO")
print("Database v4 queried: NO")
print("Database writes: NONE")
