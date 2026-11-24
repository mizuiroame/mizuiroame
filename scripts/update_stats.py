"""Build assets/stats.svg: stars, release downloads and version of each app.

Run by .github/workflows/stats.yml once a day. Standard library only.
GITHUB_TOKEN, when set, raises the API rate limit; the repos are public.
"""

from __future__ import annotations

import base64
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.request
from dataclasses import dataclass
from xml.sax.saxutils import escape

OWNER = "mizuiroame"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "stats.svg"
API = "https://api.github.com"
PER_PAGE = 100
MAX_PAGES = 10


@dataclass(frozen=True)
class App:
    repo: str
    name: str
    kind: str
    accent: str


APPS = (
    App("kaivideo", "KaiVideo", "Video player", "#FF6C9D"),
    App("kaiplayer", "KaiPlayer", "Music player", "#FF6C9D"),
    App("kairadio", "KaiRadio", "Radio and podcasts", "#4FC2F8"),
    App("kaireader", "KaiReader", "Book reader", "#F2B54A"),
    App("kaidrop", "KaiDrop", "PC to console transfers", "#5DE0A6"),
)


@dataclass(frozen=True)
class Stats:
    app: App
    stars: int
    downloads: int
    version: str


def get_json(path: str):
    request = urllib.request.Request(API + path)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", "profile-stats")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch(app: App) -> Stats:
    repo = get_json(f"/repos/{OWNER}/{app.repo}")
    releases = []
    for page in range(1, MAX_PAGES + 1):
        batch = get_json(f"/repos/{OWNER}/{app.repo}/releases?per_page={PER_PAGE}&page={page}")
        releases.extend(batch)
        if len(batch) < PER_PAGE:
            break
    downloads = sum(asset["download_count"] for rel in releases for asset in rel["assets"])
    published = [rel for rel in releases if not rel["draft"]]
    version = published[0]["tag_name"] if published else "-"
    return Stats(app, int(repo["stargazers_count"]), downloads, version)


def icon_uri(app: App) -> str:
    data = (ROOT / "assets" / "icons" / f"{app.repo}.png").read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def number(value: int) -> str:
    return f"{value:,}"


SEAL_W, SEAL_H = 58, 96  # Mizuiro's seal, faint, over the signature at the bottom right.


def seal_uri() -> str:
    data = (ROOT / "assets" / "brand-seal.png").read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def render(stats: list[Stats], today: dt.date) -> str:
    width, row_h, top = 640, 78, 156
    seal = seal_uri()
    height = top + row_h * len(stats) + 46 + SEAL_H - 30  # Room at the foot for the seal over the name.
    total_stars = sum(s.stars for s in stats)
    total_downloads = sum(s.downloads for s in stats)
    most = max((s.downloads for s in stats), default=0) or 1
    bar_x, bar_w = 316, 140

    rows = []
    for i, s in enumerate(stats):
        y = top + i * row_h
        fill = max(6, round(bar_w * s.downloads / most))
        rows.append(f"""
  <g>
    <image x="36" y="{y}" width="56" height="56" href="{icon_uri(s.app)}" clip-path="url(#round)"/>
    <text x="106" y="{y + 25}" class="name">{escape(s.app.name)}</text>
    <text x="106" y="{y + 48}" class="kind">{escape(s.app.kind)} · {escape(s.version)}</text>
    <rect x="{bar_x}" y="{y + 22}" width="{bar_w}" height="12" rx="6" class="track"/>
    <rect x="{bar_x}" y="{y + 22}" width="{fill}" height="12" rx="6" fill="{s.app.accent}"/>
    <text x="{width - 92}" y="{y + 34}" class="num" text-anchor="end">{number(s.downloads)}</text>
    <text x="{width - 28}" y="{y + 34}" class="num star" text-anchor="end">★ {number(s.stars)}</text>
  </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Kai apps: {total_stars} stars, {total_downloads} downloads">
  <title>Kai apps: {number(total_stars)} stars, {number(total_downloads)} downloads</title>
  <defs>
    <clipPath id="round" clipPathUnits="objectBoundingBox"><rect width="1" height="1" rx="0.22"/></clipPath>
    <clipPath id="card"><rect width="{width}" height="{height}" rx="18"/></clipPath>
    <radialGradient id="glow" cx="0.72" cy="0.2" r="0.75">
      <stop offset="0" stop-color="#BCE2E8" stop-opacity=".14"/>
      <stop offset="1" stop-color="#BCE2E8" stop-opacity="0"/>
    </radialGradient>
    <pattern id="lines" width="26" height="26" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="1" height="26" fill="#BCE2E8" opacity=".035"/>
    </pattern>
  </defs>
  <style>
    text {{ font-family: "Segoe UI", -apple-system, "Helvetica Neue", Arial, sans-serif; }}
    .label {{ fill: #7E8A90; font-size: 13px; font-weight: 600; letter-spacing: 2.4px; }}
    .big {{ fill: #E8F1F3; font-size: 46px; font-weight: 700; }}
    .name {{ fill: #E8F1F3; font-size: 22px; font-weight: 700; }}
    .kind {{ fill: #7E8A90; font-size: 15px; }}
    .num {{ fill: #E8F1F3; font-size: 19px; font-weight: 600; }}
    .star {{ fill: #BCE2E8; }}
    .head {{ fill: #7E8A90; font-size: 12px; font-weight: 600; letter-spacing: 2px; }}
    .foot {{ fill: #5A646A; font-size: 12px; letter-spacing: 0.3px; }}
    .sign {{ fill: #BCE2E8; font-size: 11px; font-weight: 300; letter-spacing: 4px; opacity: .7; }}
    .track {{ fill: #1C2026; }}
  </style>
  <g clip-path="url(#card)">
    <rect width="{width}" height="{height}" fill="#0C0D13"/>
    <rect width="{width}" height="{height}" fill="url(#glow)"/>
    <rect width="{width}" height="{height}" fill="url(#lines)"/>
    <rect y="{height - 3}" width="{width}" height="3" fill="#BCE2E8" opacity=".35"/>
    <image x="{width - 28 - 58 - (SEAL_W - 58) // 2 - 4}" y="{height - 40 - SEAL_H}" width="{SEAL_W}" height="{SEAL_H}" href="{seal}" opacity=".22"/>
  </g>
  <text x="36" y="46" class="label">TOTAL STARS</text>
  <text x="36" y="98" class="big"><tspan fill="#BCE2E8">★</tspan> {number(total_stars)}</text>
  <text x="316" y="46" class="label">TOTAL DOWNLOADS</text>
  <text x="316" y="98" class="big"><tspan fill="#BCE2E8">↓</tspan> {number(total_downloads)}</text>
  <text x="{width - 92}" y="{top - 16}" class="head" text-anchor="end">DOWNLOADS</text>
  <text x="{width - 28}" y="{top - 16}" class="head" text-anchor="end">★</text>
  {''.join(rows)}
  <text x="36" y="{height - 20}" class="foot">GitHub release downloads, Brewstore's included · {today.isoformat()}</text>
  <text x="{width - 28}" y="{height - 20}" class="sign" text-anchor="end">MIZUIRO</text>
</svg>
"""


def main() -> int:
    try:
        stats = [fetch(app) for app in APPS]
    except Exception as error:  # keep the last good card if GitHub fails
        print(f"Could not read GitHub: {error}", file=sys.stderr)
        return 1
    OUT.write_text(render(stats, dt.date.today()), encoding="utf-8")
    for s in stats:
        print(f"{s.app.name}: {s.version}, {s.stars} stars, {s.downloads} downloads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
