"""Build assets/header.svg, the profile banner: Mizuiro's mark (the 水色 seal and
MIZUIRO), a line about the apps, and their icons.

The mark's pieces (assets/brand-bg.png, brand-seal.png, brand-wordmark.png)
are pictures made on the PC by switch2homebrew-submit/tools/brand.py, so the
banner looks the same on every screen without its fonts; this only puts them
together, which needs nothing but the standard library.
"""

from __future__ import annotations

import base64
import sys

from update_stats import APPS, ROOT, icon_uri

OUT = ROOT / "assets" / "header.svg"
WIDTH, HEIGHT = 840, 210
ICON, ICON_STEP = 52, 62
SEAL_H = 150
WORD_H = 34


def asset_uri(name: str) -> str:
    data = (ROOT / "assets" / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def render() -> str:
    icons = []
    for i, app in enumerate(APPS):
        x = WIDTH - 36 - ICON - (len(APPS) - 1 - i) * ICON_STEP
        icons.append(
            f'<g>'
            f'<image x="{x}" y="72" width="{ICON}" height="{ICON}" href="{icon_uri(app)}" clip-path="url(#round)"/>'
            f'<rect x="{x + ICON / 2 - 10}" y="{72 + ICON + 10}" width="20" height="3" rx="1.5" fill="{app.accent}"/></g>'
        )
    seal_w = round(SEAL_H * 202 / 334)
    word_w = round(WORD_H * 611 / 122)
    text_x = 40 + seal_w + 28
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Mizuiro: homebrew apps for Nintendo Switch 2">
  <title>Mizuiro: homebrew apps for Nintendo Switch 2</title>
  <defs>
    <clipPath id="card"><rect width="{WIDTH}" height="{HEIGHT}" rx="18"/></clipPath>
    <clipPath id="round" clipPathUnits="objectBoundingBox"><rect width="1" height="1" rx="0.22"/></clipPath>
  </defs>
  <style>
    text {{ font-family: "Segoe UI", -apple-system, "Helvetica Neue", Arial, sans-serif; }}
    .sub {{ fill: #C9D2D6; font-size: 15px; letter-spacing: 0.3px; }}
    .tag {{ fill: #7E8A90; font-size: 11px; font-weight: 600; letter-spacing: 2.2px; }}
  </style>
  <g clip-path="url(#card)">
    <image width="{WIDTH}" height="{HEIGHT}" href="{asset_uri('brand-bg.png')}" preserveAspectRatio="none"/>
  </g>
  <image x="40" y="{(HEIGHT - SEAL_H) // 2}" width="{seal_w}" height="{SEAL_H}" href="{asset_uri('brand-seal.png')}"/>
  <image x="{text_x}" y="62" width="{word_w}" height="{WORD_H}" href="{asset_uri('brand-wordmark.png')}"/>
  <text x="{text_x}" y="124" class="sub">Video, music, radio, books and file transfers</text>
  <text x="{text_x}" y="146" class="sub">for Nintendo Switch 2.</text>
  <text x="{text_x}" y="172" class="tag">SWITCH 2 HOMEBREW · KAIHEN</text>
  {''.join(icons)}
</svg>
"""


def main() -> int:
    OUT.write_text(render(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
