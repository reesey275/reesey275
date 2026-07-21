#!/usr/bin/env python3
"""Tests for deterministic profile link validation."""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
import urllib.error
from typing import Any


SCRIPTS_DIR = pathlib.Path(__file__).resolve().parents[1]
PROJECT_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import check_profile_links as profile_links  # noqa: E402


class FakeResponse:
    """Small context-managed GitHub API response."""

    def __init__(self, payload: Any, status: int = 200) -> None:
        self.payload = payload
        self.status = status

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def getcode(self) -> int:
        return self.status

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class SequenceOpener:
    """Return or raise a configured response sequence."""

    def __init__(self, *responses: Any) -> None:
        self.responses = list(responses)
        self.calls = 0

    def __call__(self, request: object, timeout: float) -> FakeResponse:
        del request, timeout
        response = self.responses[self.calls]
        self.calls += 1
        if isinstance(response, BaseException):
            raise response
        return response


class MarkdownLinkTests(unittest.TestCase):
    def test_extracts_links_but_ignores_fenced_examples(self) -> None:
        text = """[Local](docs/page.md)
[reference]: https://github.com/example/public-repo
<a href="docs/other.md">Other</a>
Bare repository: https://github.com/example/second-repo.
```markdown
[ignored](docs/missing.md)
```
"""

        references = profile_links.extract_link_references(
            pathlib.Path("README.md"),
            text,
        )

        self.assertEqual(
            [reference.target for reference in references],
            [
                "docs/page.md",
                "https://github.com/example/public-repo",
                "docs/other.md",
                "https://github.com/example/second-repo",
            ],
        )

    def test_relative_validation_reports_missing_and_escaping_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory)
            docs = root / "docs"
            docs.mkdir()
            (docs / "exists.md").write_text("# Existing\n", encoding="utf-8")
            readme = root / "README.md"
            readme.write_text(
                "[Good](docs/exists.md)\n"
                "[Missing](docs/missing.md)\n"
                "[Escape](../outside.md)\n",
                encoding="utf-8",
            )
            references = profile_links.read_link_references([readme])

            errors = profile_links.validate_relative_links(root, references)

            self.assertEqual(len(errors), 2)
            self.assertIn("target does not exist", errors[0])
            self.assertIn("escapes repository root", errors[1])

    def test_repository_url_parser_skips_non_repository_github_pages(self) -> None:
        self.assertEqual(
            profile_links.github_repository_name(
                "https://github.com/example/public-repo/blob/main/README.md"
            ),
            "example/public-repo",
        )
        self.assertIsNone(
            profile_links.github_repository_name("https://github.com/features/copilot")
        )
        self.assertIsNone(
            profile_links.github_repository_name("https://github.com/example")
        )

    def test_manual_repository_counts_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory)
            readme = root / "README.md"
            readme.write_text(
                "Public work: 4 active repositories.\n",
                encoding="utf-8",
            )

            errors = profile_links.validate_repository_counts(root, [readme])

            self.assertEqual(len(errors), 1)
            self.assertIn("repository count is not allowed", errors[0])

    def test_current_profile_relative_links_exist(self) -> None:
        files = profile_links.discover_markdown_files(
            PROJECT_ROOT,
            profile_links.DEFAULT_INPUTS,
        )
        references = profile_links.read_link_references(files)

        self.assertEqual(
            profile_links.validate_relative_links(PROJECT_ROOT, references),
            [],
        )
        self.assertEqual(
            profile_links.validate_repository_counts(PROJECT_ROOT, files),
            [],
        )


class GitHubVisibilityTests(unittest.TestCase):
    def test_requires_explicit_public_visibility(self) -> None:
        opener = SequenceOpener(
            FakeResponse({"private": False, "visibility": "public"})
        )

        result = profile_links.verify_public_repository(
            "example/public-repo",
            token=None,
            attempts=3,
            timeout=1,
            opener=opener,
            sleeper=lambda _: None,
        )

        self.assertEqual(result.status, "public")
        self.assertEqual(opener.calls, 1)

    def test_rejects_explicit_non_public_visibility(self) -> None:
        opener = SequenceOpener(
            FakeResponse({"private": True, "visibility": "private"})
        )

        result = profile_links.verify_public_repository(
            "example/private-repo",
            token=None,
            attempts=3,
            timeout=1,
            opener=opener,
            sleeper=lambda _: None,
        )

        self.assertEqual(result.status, "non-public")
        self.assertEqual(opener.calls, 1)

    def test_treats_not_found_as_confirmed_inaccessible(self) -> None:
        error = urllib.error.HTTPError(
            "https://api.github.com/repos/example/missing",
            404,
            "Not Found",
            None,
            None,
        )
        opener = SequenceOpener(error)

        result = profile_links.verify_public_repository(
            "example/missing",
            token=None,
            attempts=3,
            timeout=1,
            opener=opener,
            sleeper=lambda _: None,
        )

        self.assertEqual(result.status, "inaccessible")
        self.assertEqual(opener.calls, 1)

    def test_retries_transient_failures_with_a_bound(self) -> None:
        opener = SequenceOpener(
            urllib.error.URLError("temporary failure"),
            urllib.error.URLError("temporary failure"),
            FakeResponse({"private": False, "visibility": "public"}),
        )
        sleeps: list[float] = []

        result = profile_links.verify_public_repository(
            "example/public-repo",
            token=None,
            attempts=3,
            timeout=1,
            opener=opener,
            sleeper=sleeps.append,
        )

        self.assertEqual(result.status, "public")
        self.assertEqual(opener.calls, 3)
        self.assertEqual(sleeps, [1.0, 2.0])

    def test_fails_closed_when_visibility_is_unknown(self) -> None:
        opener = SequenceOpener(FakeResponse({"private": False}))

        result = profile_links.verify_public_repository(
            "example/unknown",
            token=None,
            attempts=3,
            timeout=1,
            opener=opener,
            sleeper=lambda _: None,
        )

        self.assertEqual(result.status, "unverified")
        self.assertIn("explicitly report public", result.detail)


if __name__ == "__main__":
    unittest.main()
