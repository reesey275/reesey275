#!/usr/bin/env python3
"""Tests for the repository-hosted profile card renderer."""

from __future__ import annotations

import collections
import pathlib
import sys
import unittest
import xml.etree.ElementTree as element_tree


SCRIPTS_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_profile_stats as profile_stats  # noqa: E402


class ProfileStatsRendererTests(unittest.TestCase):
    def test_stats_card_contains_expected_public_metrics(self) -> None:
        stats = {
            "commits": 235,
            "followers": 17,
            "issues": 700,
            "name": "Mr. Potato",
            "public_repositories": 4,
            "pull_requests": 1358,
            "stars": 5,
            "username": "reesey275",
            "year": 2026,
        }

        card = profile_stats.render_stats_card(stats, "2026-07-21 UTC")

        element_tree.fromstring(card)
        self.assertIn("Mr. Potato's GitHub Stats", card)
        self.assertIn("Public Commits (2026)", card)
        self.assertIn(">1358<", card)
        self.assertNotIn("<script", card)
        self.assertNotIn("https://", card)
        self.assertNotIn("href=", card)

    def test_languages_card_orders_languages_by_bytes(self) -> None:
        languages = collections.Counter(
            {
                "JavaScript": 200,
                "Python": 500,
                "Shell": 300,
            }
        )

        card = profile_stats.render_languages_card(
            languages,
            "2026-07-21 UTC",
        )

        element_tree.fromstring(card)
        self.assertLess(card.index("Python"), card.index("Shell"))
        self.assertLess(card.index("Shell"), card.index("JavaScript"))
        self.assertIn("50.0%", card)
        self.assertIn("30.0%", card)
        self.assertIn("20.0%", card)


if __name__ == "__main__":
    unittest.main()
