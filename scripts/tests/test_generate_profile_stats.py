#!/usr/bin/env python3
"""Tests for the repository-hosted profile card renderer."""

from __future__ import annotations

import collections
import pathlib
import sys
import unittest
import xml.etree.ElementTree as element_tree
from typing import Any


SCRIPTS_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_profile_stats as profile_stats  # noqa: E402


class FakeGitHubClient:
    """Return a mixture of public, private, fork, and profile repositories."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def get(
        self,
        path: str,
        params: dict[str, str | int] | None = None,
    ) -> Any:
        self.calls.append(path)
        if path == "/users/reesey275":
            return {
                "followers": 17,
                "name": "Mr. Potato",
                "public_repos": 3,
            }
        if path == "/users/reesey275/repos":
            return [
                {
                    "fork": False,
                    "full_name": "reesey275/public-project",
                    "name": "public-project",
                    "owner": {"login": "reesey275"},
                    "private": False,
                    "stargazers_count": 4,
                    "visibility": "public",
                },
                {
                    "fork": False,
                    "full_name": "reesey275/reesey275",
                    "name": "reesey275",
                    "owner": {"login": "reesey275"},
                    "private": False,
                    "stargazers_count": 1,
                    "visibility": "public",
                },
                {
                    "fork": True,
                    "full_name": "reesey275/public-fork",
                    "name": "public-fork",
                    "owner": {"login": "reesey275"},
                    "private": False,
                    "stargazers_count": 99,
                    "visibility": "public",
                },
                {
                    "fork": False,
                    "full_name": "reesey275/private-project",
                    "name": "private-project",
                    "owner": {"login": "reesey275"},
                    "private": True,
                    "stargazers_count": 99,
                    "visibility": "private",
                },
            ]
        if path == "/repos/reesey275/public-project/languages":
            return {"Python": 500, "Shell": 300}
        raise AssertionError(f"Unexpected GitHub API request: {path} {params}")


class ProfileStatsRendererTests(unittest.TestCase):
    def test_collection_uses_only_approved_public_sources(self) -> None:
        client = FakeGitHubClient()

        stats, languages = profile_stats.collect_profile_data(
            client,
            "reesey275",
        )

        self.assertEqual(stats["stars"], 5)
        self.assertEqual(stats["public_repositories"], 3)
        self.assertEqual(stats["followers"], 17)
        self.assertEqual(languages, {"Python": 500, "Shell": 300})
        self.assertNotIn("/repos/reesey275/reesey275/languages", client.calls)
        self.assertNotIn("/repos/reesey275/public-fork/languages", client.calls)
        self.assertNotIn("/repos/reesey275/private-project/languages", client.calls)
        self.assertFalse(any(path.startswith("/search/") for path in client.calls))

    def test_stats_card_contains_only_unambiguously_public_metrics(self) -> None:
        stats = {
            "followers": 17,
            "name": "Mr. Potato",
            "public_repositories": 4,
            "stars": 5,
            "username": "reesey275",
        }

        card = profile_stats.render_stats_card(
            stats,
            "2026-07-21 12:00 UTC",
        )

        root = element_tree.fromstring(card)
        self.assertEqual(root.attrib["width"], "495")
        self.assertEqual(root.attrib["height"], "210")
        self.assertIn("Mr. Potato's Public GitHub Summary", card)
        self.assertIn("Stars on public source repositories", card)
        self.assertIn("Public GitHub REST data", card)
        self.assertIn("Stars exclude forks", card)
        self.assertIn("Last successful refresh 2026-07-21 12:00 UTC", card)
        self.assertNotIn("Public Commits", card)
        self.assertNotIn("Pull Requests", card)
        self.assertNotIn("Issues Opened", card)
        self.assertNotIn("<script", card)
        self.assertNotIn("https://", card)
        self.assertNotIn("href=", card)

    def test_code_composition_orders_languages_and_explains_scope(self) -> None:
        languages = collections.Counter(
            {
                "JavaScript": 200,
                "Python": 500,
                "Shell": 300,
            }
        )

        card = profile_stats.render_languages_card(
            languages,
            "2026-07-21 12:00 UTC",
        )

        root = element_tree.fromstring(card)
        self.assertEqual(root.attrib["width"], "495")
        self.assertEqual(root.attrib["height"], "340")
        self.assertLess(card.index("Python"), card.index("Shell"))
        self.assertLess(card.index("Shell"), card.index("JavaScript"))
        self.assertIn("50.0%", card)
        self.assertIn("30.0%", card)
        self.assertIn("20.0%", card)
        self.assertIn("Public Project Code Composition", card)
        self.assertIn("GitHub Linguist", card)
        self.assertIn("Profile repository excluded", card)
        self.assertIn("Not a proficiency ranking", card)

    def test_code_composition_reserves_space_below_six_rows(self) -> None:
        languages = collections.Counter(
            {
                "Python": 600,
                "JavaScript": 500,
                "Shell": 400,
                "HTML": 300,
                "CSS": 200,
                "Makefile": 100,
            }
        )

        card = profile_stats.render_languages_card(
            languages,
            "2026-07-21 12:00 UTC",
        )

        last_bar_bottom = 82 + (6 - 1) * 34 + 8 + 5
        footer_y = 292
        self.assertGreaterEqual(footer_y - last_bar_bottom, 27)
        self.assertIn(f'y="{last_bar_bottom - 5}" width="445"', card)
        self.assertIn(f'<text x="25" y="{footer_y}" class="muted">', card)


if __name__ == "__main__":
    unittest.main()
