import datetime as dt
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import make_header  # noqa: E402
import update_stats as us  # noqa: E402


def sample(downloads: tuple[int, ...]) -> list[us.Stats]:
    return [us.Stats(app, i + 1, d, f"v1.{i}.0") for i, (app, d) in enumerate(zip(us.APPS, downloads))]


class RenderTest(unittest.TestCase):
    def test_stats_card_is_valid_svg_with_totals(self) -> None:
        svg = us.render(sample((1200, 300, 0, 0, 45)), dt.date(2026, 11, 23))
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn("1,545", svg)
        self.assertIn("</tspan> 15</text>", svg)
        self.assertIn("· 2026-11-23", svg)
        for app in us.APPS:
            self.assertIn(app.name, svg)

    def test_no_downloads_still_draws_bars(self) -> None:
        svg = us.render(sample((0, 0, 0, 0, 0)), dt.date(2026, 1, 1))
        ET.fromstring(svg)
        self.assertIn('width="6"', svg)

    def test_text_is_escaped(self) -> None:
        stats = [us.Stats(us.App("kaivideo", "A<B", "x&y", "#fff"), 0, 0, "v<1>")]
        ET.fromstring(us.render(stats, dt.date(2026, 1, 1)))

    def test_header_is_valid_svg(self) -> None:
        root = ET.fromstring(make_header.render())
        self.assertTrue(root.tag.endswith("svg"))


class FetchTest(unittest.TestCase):
    def test_sums_every_asset_and_takes_newest_tag(self) -> None:
        pages = {
            "/repos/mizuiroame/kaivideo": {"stargazers_count": 7},
            "/repos/mizuiroame/kaivideo/releases?per_page=100&page=1": [
                {"draft": False, "tag_name": "v2", "assets": [{"download_count": 5}, {"download_count": 3}]},
                {"draft": False, "tag_name": "v1", "assets": [{"download_count": 10}]},
            ],
        }
        original = us.get_json
        us.get_json = pages.__getitem__
        try:
            stats = us.fetch(us.APPS[0])
        finally:
            us.get_json = original
        self.assertEqual((stats.stars, stats.downloads, stats.version), (7, 18, "v2"))


if __name__ == "__main__":
    unittest.main()
