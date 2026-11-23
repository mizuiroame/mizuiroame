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


def render(stats: list[Stats], today: dt.date) -> str:
    width, row_h, top = 840, 76, 150
    height = top + row_h * len(stats) + 46
    total_stars = sum(s.stars for s in stats)
    total_downloads = sum(s.downloads for s in stats)
    most = max((s.downloads for s in stats), default=0) or 1
    bar_x, bar_w = 300, 330

    rows = []
    for i, s in enumerate(stats):
        y = top + i * row_h
        fill = max(6, round(bar_w * s.downloads / most))
        rows.append(f"""
  <g>
    <image x="36" y="{y}" width="56" height="56" href="{icon_uri(s.app)}" clip-path="url(#round)"/>
    <text x="110" y="{y + 25}" class="name">{escape(s.app.name)}</text>
    <text x="110" y="{y + 47}" class="kind">{escape(s.app.kind)} · {escape(s.version)}</text>
    <rect x="{bar_x}" y="{y + 22}" width="{bar_w}" height="12" rx="6" class="track"/>
    <rect x="{bar_x}" y="{y + 22}" width="{fill}" height="12" rx="6" fill="{s.app.accent}"/>
    <text x="{width - 120}" y="{y + 33}" class="num" text-anchor="end">{number(s.downloads)}</text>
    <text x="{width - 36}" y="{y + 33}" class="num star" text-anchor="end">★ {number(s.stars)}</text>
  </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Kai apps: {total_stars} stars, {total_downloads} downloads">
  <title>Kai apps: {number(total_stars)} stars, {number(total_downloads)} downloads</title>
  <defs>
    <clipPath id="round" clipPathUnits="objectBoundingBox"><rect width="1" height="1" rx="0.22"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#2C2D32"/>
      <stop offset="1" stop-color="#1E1F24"/>
    </linearGradient>
  </defs>
  <style>
    text {{ font-family: "Segoe UI", -apple-system, "Helvetica Neue", Arial, sans-serif; }}
    .label {{ fill: #8B8D98; font-size: 13px; font-weight: 600; letter-spacing: 1.5px; }}
    .big {{ fill: #F4F4F6; font-size: 40px; font-weight: 700; }}
    .name {{ fill: #F4F4F6; font-size: 19px; font-weight: 700; }}
    .kind {{ fill: #8B8D98; font-size: 13px; }}
    .num {{ fill: #F4F4F6; font-size: 16px; font-weight: 600; }}
    .star {{ fill: #FFD166; }}
    .head {{ fill: #8B8D98; font-size: 12px; font-weight: 600; letter-spacing: 1px; }}
    .foot {{ fill: #62646E; font-size: 12px; }}
    .track {{ fill: #3A3B42; }}
  </style>
  <rect width="{width}" height="{height}" rx="18" fill="url(#bg)"/>
  <path d="M{width - 260} 0 L{width} 0 L{width} {height} L{width - 260 - height} {height} Z" fill="#000" opacity=".12"/>
  <text x="36" y="46" class="label">TOTAL STARS</text>
  <text x="36" y="94" class="big"><tspan fill="#FFD166">★</tspan> {number(total_stars)}</text>
  <text x="300" y="46" class="label">TOTAL DOWNLOADS</text>
  <text x="300" y="94" class="big"><tspan fill="#4FC2F8">↓</tspan> {number(total_downloads)}</text>
  <text x="{width - 120}" y="{top - 14}" class="head" text-anchor="end">DOWNLOADS</text>
  <text x="{width - 36}" y="{top - 14}" class="head" text-anchor="end">STARS</text>
  {''.join(rows)}
  <text x="36" y="{height - 20}" class="foot">Release downloads on GitHub, Brewstore installs included · updated {today.isoformat()}</text>
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
