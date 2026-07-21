#!/usr/bin/env python3
"""Tests for the repository-hosted WakaTime dashboard renderer."""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
import xml.etree.ElementTree as element_tree


SCRIPTS_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_waka_dashboard as dashboard  # noqa: E402


def summary_day(
    date: str,
    total_seconds: int,
    languages: list[dict[str, object]],
    projects: list[dict[str, object]],
) -> dict[str, object]:
    """Build one small WakaTime summary day."""

    return {
        "range": {"date": date, "timezone": "America/New_York"},
        "grand_total": {"total_seconds": total_seconds},
        "languages": languages,
        "editors": [{"name": "VS Code", "total_seconds": total_seconds}],
        "operating_systems": [
            {"name": "Windows", "total_seconds": total_seconds}
        ],
        "projects": projects,
        "categories": [{"name": "Coding", "total_seconds": total_seconds}],
    }


class WakaDashboardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = {
            "data": [
                summary_day(
                    "2026-07-15",
                    3600,
                    [
                        {"name": "Python", "total_seconds": 2400},
                        {"name": "Markdown", "total_seconds": 1200},
                    ],
                    [{"name": "TAGS_[Core]", "total_seconds": 3600}],
                ),
                summary_day(
                    "2026-07-16",
                    7200,
                    [
                        {"name": "Python", "total_seconds": 3600},
                        {"name": "PowerShell", "total_seconds": 2400},
                        {"name": "Other", "total_seconds": 1200},
                    ],
                    [{"name": "TAGS_[Core]", "total_seconds": 5400}],
                ),
                summary_day("2026-07-17", 0, [], []),
            ]
        }
        self.data = dashboard.dashboard_from_summaries(self.payload)

    def test_summaries_are_aggregated_for_cards_and_daily_chart(self) -> None:
        self.assertEqual(self.data.total_seconds, 10800)
        self.assertEqual(self.data.daily_average_seconds, 3600)
        self.assertEqual(self.data.best_day.date.isoformat(), "2026-07-16")
        self.assertEqual(self.data.languages[0].name, "Python")
        self.assertAlmostEqual(self.data.languages[0].percent, 55.56, places=2)
        self.assertEqual(len(self.data.daily), 3)

    def test_svg_is_self_contained_and_accessible(self) -> None:
        card = dashboard.render_svg(self.data, "2026-07-21 12:00:00 UTC")

        element_tree.fromstring(card)
        self.assertIn("Weekly WakaTime Development Dashboard", card)
        self.assertIn("3 calendar days", card)
        self.assertIn("Daily activity", card)
        self.assertIn("TAGS_[Core]", card)
        self.assertNotIn("<script", card)
        self.assertNotIn("href=", card)
        self.assertNotIn("https://", card)

    def test_markdown_is_collapsed_and_escapes_metric_names(self) -> None:
        markdown = dashboard.render_markdown(
            self.data,
            "2026-07-21 12:00:00 UTC",
        )

        self.assertIn("wakatime-dashboard.svg", markdown)
        self.assertIn("<details>", markdown)
        self.assertIn("<summary>View detailed weekly data</summary>", markdown)
        self.assertIn(r"TAGS\_\[Core\]", markdown)
        self.assertIn("55.56%", markdown)

    def test_readme_update_preserves_markers_and_surrounding_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            readme = pathlib.Path(directory) / "README.md"
            readme.write_text(
                "Before\n<!--START_SECTION:waka-->\nOld\n"
                "<!--END_SECTION:waka-->\nAfter\n",
                encoding="utf-8",
            )

            dashboard.update_readme(readme, "New dashboard")

            content = readme.read_text(encoding="utf-8")
            self.assertEqual(content.count(dashboard.START_MARKER), 1)
            self.assertEqual(content.count(dashboard.END_MARKER), 1)
            self.assertIn("Before\n", content)
            self.assertIn("\nNew dashboard\n", content)
            self.assertTrue(content.endswith("After\n"))

    def test_snapshot_renders_honest_first_refresh_fallback(self) -> None:
        snapshot = {
            "snapshot": {
                "timezone": "America/New_York",
                "start": "2026-07-14",
                "end": "2026-07-21",
                "total_seconds": 176631,
                "daily_average_seconds": 22078,
                "best_day": {
                    "date": "2026-07-17",
                    "total_seconds": 41880,
                },
                "daily": [],
                "languages": [],
                "editors": [],
                "operating_systems": [],
                "projects": [],
                "categories": [],
            }
        }
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "snapshot.json"
            path.write_text(json.dumps(snapshot), encoding="utf-8")

            data = dashboard.load_dashboard(path)
            card = dashboard.render_svg(data, "2026-07-21 12:00:00 UTC")

        self.assertIn("First automated refresh pending", card)
        self.assertIn("49 hrs 3 mins total", card)


if __name__ == "__main__":
    unittest.main()
