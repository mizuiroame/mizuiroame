"""Build assets/header.svg, the profile banner, with the app icons inside it."""

from __future__ import annotations

import sys

from update_stats import APPS, ROOT, icon_uri

OUT = ROOT / "assets" / "header.svg"
WIDTH, HEIGHT = 840, 210


def render() -> str:
    icons = []
    for i, app in enumerate(APPS):
        x = WIDTH - 36 - 64 - (len(APPS) - 1 - i) * 78
        icons.append(
            f'<g>'
            f'<image x="{x}" y="73" width="64" height="64" href="{icon_uri(app)}" clip-path="url(#round)"/>'
            f'<rect x="{x + 20}" y="146" width="24" height="4" rx="2" fill="{app.accent}"/></g>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Mizuiro: homebrew apps for Nintendo Switch 2">
  <title>Mizuiro: homebrew apps for Nintendo Switch 2</title>
  <defs>
    <clipPath id="round" clipPathUnits="objectBoundingBox"><rect width="1" height="1" rx="0.22"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#2C2D32"/>
      <stop offset="1" stop-color="#1E1F24"/>
    </linearGradient>
    <linearGradient id="ink" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#A0D8EF"/>
      <stop offset="1" stop-color="#4FC2F8"/>
    </linearGradient>
  </defs>
  <style>
    text {{ font-family: "Segoe UI", -apple-system, "Helvetica Neue", Arial, sans-serif; }}
    .title {{ font-size: 58px; font-weight: 800; letter-spacing: -1px; }}
    .sub {{ fill: #C9CAD1; font-size: 18px; }}
    .tag {{ fill: #8B8D98; font-size: 13px; font-weight: 600; letter-spacing: 1.5px; }}
  </style>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="18" fill="url(#bg)"/>
  <path d="M300 0 L{WIDTH} 0 L{WIDTH} {HEIGHT} L{300 + HEIGHT} {HEIGHT} Z" fill="#000" opacity=".10"/>
  <text x="40" y="58" class="tag">SWITCH 2 HOMEBREW · KAIHEN</text>
  <text x="38" y="122" class="title" fill="url(#ink)">Mizuiro</text>
  <text x="40" y="160" class="sub">Video, music, radio, books and file transfers,</text>
  <text x="40" y="184" class="sub">made to feel at home on the console.</text>
  {''.join(icons)}
</svg>
"""


def main() -> int:
    OUT.write_text(render(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
