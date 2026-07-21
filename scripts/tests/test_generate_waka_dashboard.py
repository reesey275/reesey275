#!/usr/bin/env python3
"""Tests for the repository-hosted WakaTime dashboard renderer."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as element_tree


SCRIPTS_DIR = pathlib.Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_waka_dashboard as dashboard  # noqa: E402


def workflow_run_script(step_name: str) -> str:
    """Extract one run block without adding a YAML dependency to the tests."""

    workflow = REPOSITORY_ROOT / ".github" / "workflows" / "waka-readme.yml"
    lines = workflow.read_text(encoding="utf-8").splitlines()
    step_index = lines.index(f"      - name: {step_name}")
    run_index = lines.index("        run: |", step_index)
    script: list[str] = []
    for line in lines[run_index + 1 :]:
        if line.startswith("      - name: "):
            break
        script.append(line[10:] if line.startswith("          ") else "")
    return "\n".join(script)


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
                summary_day("2026-07-18", 0, [], []),
                summary_day("2026-07-19", 0, [], []),
                summary_day("2026-07-20", 0, [], []),
                summary_day("2026-07-21", 0, [], []),
            ]
        }
        self.data = dashboard.dashboard_from_summaries(self.payload)

    def test_summaries_are_aggregated_for_cards_and_daily_chart(self) -> None:
        self.assertEqual(self.data.total_seconds, 10800)
        self.assertAlmostEqual(
            self.data.daily_average_seconds,
            10800 / dashboard.REPORTING_DAYS,
        )
        self.assertEqual(self.data.best_day.date.isoformat(), "2026-07-16")
        self.assertEqual(self.data.languages[0].name, "Python")
        self.assertAlmostEqual(self.data.languages[0].percent, 55.56, places=2)
        self.assertEqual(len(self.data.daily), dashboard.REPORTING_DAYS)

    def test_svg_is_self_contained_and_accessible(self) -> None:
        card = dashboard.render_svg(self.data, "2026-07-21 12:00:00 UTC")

        element_tree.fromstring(card)
        self.assertIn("Seven-Day WakaTime Editor Activity", card)
        self.assertIn("7 calendar days", card)
        self.assertIn("Daily editor activity", card)
        self.assertIn("Editors", card)
        self.assertIn("VS Code", card)
        self.assertNotIn("TAGS_[Core]", card)
        self.assertNotIn(">Projects<", card)
        self.assertIn("not a productivity or skill score", card)
        self.assertIn("not authorship measures", card)
        self.assertIn("Last successful refresh", card)
        self.assertNotIn("<script", card)
        self.assertNotIn("href=", card)
        self.assertNotIn("https://", card)

    def test_svg_validation_checks_markup_without_rejecting_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "card.svg"
            path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg">'
                "<text>A harmless href= label</text></svg>",
                encoding="utf-8",
            )

            dashboard.validate_svg(path)

            path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<a href="https://example.com"><text>Link</text></a></svg>',
                encoding="utf-8",
            )
            with self.assertRaises(dashboard.DashboardDataError):
                dashboard.validate_svg(path)

            path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" '
                'xmlns:xlink="http://www.w3.org/1999/xlink">'
                '<image xlink:href="data:image/png;base64,AA=="/></svg>',
                encoding="utf-8",
            )
            with self.assertRaises(dashboard.DashboardDataError):
                dashboard.validate_svg(path)

            path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"><script/></svg>',
                encoding="utf-8",
            )
            with self.assertRaises(dashboard.DashboardDataError):
                dashboard.validate_svg(path)

    def test_workflow_preserves_last_dashboard_when_wakatime_is_unavailable(
        self,
    ) -> None:
        script = workflow_run_script("Fetch WakaTime stats and update dashboard")
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            profile = root / "profile"
            fake_bin = root / "bin"
            profile.mkdir()
            fake_bin.mkdir()

            readme = root / "README.md"
            card = profile / "wakatime-dashboard.svg"
            environment_file = root / "github_env"
            readme.write_text("last successful README\n", encoding="utf-8")
            card.write_text("<svg>last successful card</svg>\n", encoding="utf-8")

            fake_curl = fake_bin / "curl"
            fake_curl.write_text("#!/bin/sh\nexit 22\n", encoding="utf-8")
            fake_curl.chmod(0o755)

            environment = os.environ.copy()
            environment.update(
                {
                    "GITHUB_ENV": str(environment_file),
                    "PATH": f"{fake_bin}:{environment['PATH']}",
                    "WAKATIME_API_KEY": "unavailable",
                    "WAKATIME_TIMEZONE": "America/New_York",
                }
            )
            result = subprocess.run(
                ["bash", "-c", script],
                cwd=root,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                readme.read_text(encoding="utf-8"),
                "last successful README\n",
            )
            self.assertEqual(
                card.read_text(encoding="utf-8"),
                "<svg>last successful card</svg>\n",
            )
            self.assertEqual(
                environment_file.read_text(encoding="utf-8"),
                "WAKA_REFRESHED=false\n",
            )
            self.assertIn("Keeping the last successful dashboard", result.stdout)

    def test_markdown_is_collapsed_and_escapes_metric_names(self) -> None:
        markdown = dashboard.render_markdown(
            self.data,
            "2026-07-21 12:00:00 UTC",
        )

        self.assertIn("wakatime-dashboard.svg", markdown)
        self.assertIn("<details>", markdown)
        self.assertIn(
            "<summary>View seven-day editor activity data</summary>",
            markdown,
        )
        self.assertIn("7 inclusive calendar dates", markdown)
        self.assertEqual(
            dashboard.markdown_text("TAGS_[Core]"),
            r"TAGS\_\[Core\]",
        )
        self.assertNotIn("### Projects", markdown)
        self.assertNotIn("TAGS_[Core]", markdown)
        self.assertIn("55.56%", markdown)
        self.assertIn("do not measure authorship", markdown)
        self.assertIn("Last successful refresh", markdown)

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
                "start": "2026-07-15",
                "end": "2026-07-21",
                "total_seconds": 176631,
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

    def test_snapshot_daily_samples_are_sorted_chronologically(self) -> None:
        snapshot = {
            "snapshot": {
                "timezone": "America/New_York",
                "start": "2026-07-15",
                "end": "2026-07-21",
                "total_seconds": 10800,
                "best_day": {
                    "date": "2026-07-17",
                    "total_seconds": 7200,
                },
                "daily": [
                    {"date": "2026-07-17", "total_seconds": 7200},
                    {"date": "2026-07-15", "total_seconds": 3600},
                    {"date": "2026-07-16", "total_seconds": 0},
                    {"date": "2026-07-21", "total_seconds": 0},
                    {"date": "2026-07-19", "total_seconds": 0},
                    {"date": "2026-07-20", "total_seconds": 0},
                    {"date": "2026-07-18", "total_seconds": 0},
                ],
                "languages": [],
                "editors": [],
                "operating_systems": [],
                "projects": [],
                "categories": [],
            }
        }

        data = dashboard.dashboard_from_snapshot(snapshot)

        self.assertEqual(
            [day.date.isoformat() for day in data.daily],
            [
                "2026-07-15",
                "2026-07-16",
                "2026-07-17",
                "2026-07-18",
                "2026-07-19",
                "2026-07-20",
                "2026-07-21",
            ],
        )

    def test_summaries_reject_non_seven_day_windows(self) -> None:
        payload = {
            "data": [
                summary_day(
                    f"2026-07-{day:02d}",
                    0,
                    [],
                    [],
                )
                for day in range(14, 22)
            ]
        }

        with self.assertRaisesRegex(
            dashboard.DashboardDataError,
            "exactly 7 inclusive calendar dates",
        ):
            dashboard.dashboard_from_summaries(payload)

    def test_snapshot_rejects_legacy_eight_date_windows(self) -> None:
        snapshot = {
            "snapshot": {
                "timezone": "America/New_York",
                "start": "2026-07-14",
                "end": "2026-07-21",
                "total_seconds": 176631,
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

        with self.assertRaisesRegex(
            dashboard.DashboardDataError,
            "exactly 7 inclusive calendar dates",
        ):
            dashboard.dashboard_from_snapshot(snapshot)

    def test_summaries_reject_missing_reporting_dates(self) -> None:
        payload = {
            "data": [
                summary_day(date, 0, [], [])
                for date in (
                    "2026-07-15",
                    "2026-07-16",
                    "2026-07-17",
                    "2026-07-18",
                    "2026-07-20",
                    "2026-07-20",
                    "2026-07-21",
                )
            ]
        }

        with self.assertRaisesRegex(
            dashboard.DashboardDataError,
            "consecutive reporting date",
        ):
            dashboard.dashboard_from_summaries(payload)

    def test_workflow_requests_and_validates_seven_inclusive_dates(self) -> None:
        script = workflow_run_script("Fetch WakaTime stats and update dashboard")

        self.assertIn('TZ="$WAKATIME_TIMEZONE" date +%Y-%m-%d', script)
        self.assertIn('date -d "$END_DATE - 6 days"', script)
        self.assertIn('--data-urlencode "timezone=$WAKATIME_TIMEZONE"', script)
        self.assertIn('--expected-start "$START_DATE"', script)
        self.assertIn('--expected-end "$END_DATE"', script)


if __name__ == "__main__":
    unittest.main()
