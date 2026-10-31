"""Offline regression checks for activity statistics and honest SVG output.

Run with: python3 -m unittest discover -s tools -p 'test_*.py'
"""

import contextlib
import datetime as dt
import io
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

import activity


SVG = "{http://www.w3.org/2000/svg}"
SYNCED = "2026-10-29 04:17 UTC"


class ActivityStatisticsTests(unittest.TestCase):
    def test_missing_calendar_day_breaks_streak(self):
        # The 26th is absent, not an implied continuation of the prior run.
        days = {
            dt.date(2026, 10, 24): 2,
            dt.date(2026, 10, 25): 4,
            dt.date(2026, 10, 27): 3,
            dt.date(2026, 10, 28): 0,
        }
        stats = activity.summarize(days)
        self.assertEqual(stats["total"], 9)
        self.assertEqual(stats["current"], 1)
        self.assertEqual(stats["longest"], 2)

    def test_no_contributions_today_preserves_yesterdays_streak(self):
        days = {
            dt.date(2026, 10, 27): 2,
            dt.date(2026, 10, 28): 3,
            dt.date(2026, 10, 29): 0,
        }
        stats = activity.summarize(days)
        self.assertEqual((stats["current"], stats["longest"]), (2, 2))
        days[dt.date(2026, 10, 30)] = 0
        stats = activity.summarize(days)
        self.assertEqual((stats["current"], stats["longest"]), (0, 2))

    def test_graphql_calendar_total_is_preserved(self):
        # The API's aggregate is authoritative, even for a partial saved export.
        stats = activity.summarize({dt.date(2026, 10, 29): 7}, total=42)
        self.assertEqual(stats["total"], 42)


class ActivityRenderingTests(unittest.TestCase):
    def render_variants(self, stats, mode):
        for theme in ("dark", "light"):
            for compact in (False, True):
                with self.subTest(theme=theme, compact=compact, mode=mode):
                    root = ET.fromstring(activity.render(
                        theme, stats, "Ak1ra00", mode, SYNCED, compact=compact,
                    ).render())
                    self.assertEqual(root.tag, SVG + "svg")
                    expected = ("440", "500") if compact else ("880", "360")
                    self.assertEqual((root.get("width"), root.get("height")), expected)
                    yield root

    def test_single_week_calendar_renders_without_division_by_zero(self):
        # A one-day export was sufficient to crash the former graph renderer.
        stats = activity.summarize({dt.date(2026, 10, 29): 7})
        for root in self.render_variants(stats, "live"):
            description = root.findtext(SVG + "desc")
            self.assertIn("7 in total", description)
            self.assertIn("a current streak of 1", description)
            self.assertNotIn("DEMO DATA", description)

    def test_zero_calendar_does_not_claim_pending_or_demo_data(self):
        stats = activity.summarize({dt.date(2026, 10, 29): 0})
        self.assertEqual((stats["total"], stats["current"], stats["longest"]), (0, 0, 0))
        for root in self.render_variants(stats, "live"):
            description = root.findtext(SVG + "desc")
            self.assertIn("0 in total", description)
            self.assertNotIn("pending", description)
            self.assertNotIn("DEMO DATA", description)

    def test_placeholder_reports_missing_data_without_inventing_totals(self):
        for root in self.render_variants(None, "placeholder"):
            description = root.findtext(SVG + "desc")
            self.assertIn("first sync is pending", description)
            self.assertNotIn("in total", description)
            self.assertNotIn("DEMO DATA", description)

    def test_demo_cli_generates_all_variants_with_explicit_disclosure(self):
        # Exercise the public entry point and persisted outputs, not only render().
        with tempfile.TemporaryDirectory(prefix="activity-test-") as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                activity.main(["--demo", "--out", directory])
            outputs = sorted(Path(directory).glob("*.svg"))
            self.assertEqual({path.name for path in outputs}, {
                "activity-dark.svg", "activity-light.svg",
                "activity-dark-compact.svg", "activity-light-compact.svg",
            })
            for path in outputs:
                with self.subTest(output=path.name):
                    root = ET.parse(path).getroot()
                    self.assertTrue(root.findtext(SVG + "desc").startswith(
                        "DEMO DATA, not real activity. "))

    def test_demo_cli_refuses_production_assets(self):
        with self.assertRaisesRegex(SystemExit, "must never land in assets"):
            activity.main(["--demo", "--out", activity.ASSETS])


if __name__ == "__main__":
    unittest.main()
