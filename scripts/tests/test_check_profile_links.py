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

    def test_prohibited_profile_claims_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory)
            readme = root / "README.md"
            readme.write_text(
                "Recent: project reached 95% coverage with PortalSDK.\n",
                encoding="utf-8",
            )

            errors = profile_links.validate_profile_claims(root, [readme])

            self.assertEqual(len(errors), 3)
            self.assertTrue(
                any("stale relative-date label" in error for error in errors)
            )
            self.assertTrue(
                any("unsupported percentage claim" in error for error in errors)
            )
            self.assertTrue(
                any("removed private-project reference" in error for error in errors)
            )

    def test_profile_claim_validation_ignores_fenced_examples(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory)
            readme = root / "README.md"
            readme.write_text(
                "```markdown\nRecent: old 95% claim\n```\n",
                encoding="utf-8",
            )

            errors = profile_links.validate_profile_claims(root, [readme])

            self.assertEqual(errors, [])

    def test_profile_claim_validation_ignores_generated_waka_section(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory)
            readme = root / "README.md"
            readme.write_text(
                "<!--START_SECTION:waka-->\n"
                "Measured category: 95%\n"
                "<!--END_SECTION:waka-->\n",
                encoding="utf-8",
            )

            errors = profile_links.validate_profile_claims(root, [readme])

            self.assertEqual(errors, [])

    def test_stack_history_completeness_claims_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory)
            readme = root / "README.md"
            readme.write_text(
                "Complete Stack History — Full technology exposure\n",
                encoding="utf-8",
            )

            errors = profile_links.validate_profile_claims(root, [readme])

            self.assertEqual(len(errors), 2)
            self.assertTrue(
                all(
                    "overstated stack-history completeness" in error
                    for error in errors
                )
            )

    def test_retired_profile_paths_must_remain_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory)
            retired = root / "docs" / "PROJECTS" / "retired.md"
            retired.parent.mkdir(parents=True)
            retired.write_text("# Retired\n", encoding="utf-8")

            errors = profile_links.validate_retired_profile_paths(
                root,
                ["docs/PROJECTS/retired.md"],
            )

            self.assertEqual(len(errors), 1)
            self.assertIn("must remain absent", errors[0])

    def test_required_owner_approved_content_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = pathlib.Path(temporary_directory)
            readme = root / "README.md"
            readme.write_text("Approved contact\n", encoding="utf-8")

            errors = profile_links.validate_required_profile_content(
                root,
                {"README.md": ("Approved contact", "Approved location")},
            )

            self.assertEqual(len(errors), 1)
            self.assertIn("Approved location", errors[0])

    def test_discovery_rejects_symlinked_markdown_outside_root(self) -> None:
        with (
            tempfile.TemporaryDirectory() as repository_directory,
            tempfile.TemporaryDirectory() as outside_directory,
        ):
            root = pathlib.Path(repository_directory)
            docs = root / "docs"
            docs.mkdir()
            outside_markdown = pathlib.Path(outside_directory) / "outside.md"
            outside_markdown.write_text("# Outside\n", encoding="utf-8")
            (docs / "escaped.md").symlink_to(outside_markdown)

            with self.assertRaisesRegex(ValueError, "escapes repository root"):
                profile_links.discover_markdown_files(root, ["docs"])

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
        self.assertEqual(
            profile_links.validate_profile_claims(PROJECT_ROOT, files),
            [],
        )
        self.assertEqual(
            profile_links.validate_retired_profile_paths(PROJECT_ROOT),
            [],
        )
        self.assertEqual(
            profile_links.validate_required_profile_content(PROJECT_ROOT),
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
