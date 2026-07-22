#!/usr/bin/env python3
"""Validate local profile links and public GitHub repository targets."""

from __future__ import annotations

import argparse
import dataclasses
import html
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any


DEFAULT_INPUTS = (
    "README.md",
    "resume/resume.md",
    "docs/PROJECTS",
    "docs/STACK_HISTORY.md",
    "PHILOSOPHY.md",
)
RETIRED_PROFILE_PATHS = (
    "docs/PROJECTS/tags-mcp-servers.md",
    "ENVIRONMENT.md",
)
REQUIRED_PROFILE_SNIPPETS: Mapping[str, tuple[str, ...]] = {
    "README.md": (
        "AI-assisted solo human operator",
        "reesey.chad@outlook.com",
        "Space Coast, Florida, United States",
        "## Demonstrated Capabilities",
        "JavaScript and Node.js",
        "API Development",
        "Java — Current Learning",
        "Documentation, Validation, and Engineering Governance",
    ),
    "resume/resume.md": (
        "August 10, 2000–March 28, 2012",
        "AI-assisted solo human operator",
        "reesey.chad@outlook.com",
        "Space Coast, Florida, United States",
        "Demonstrated Capabilities and Supporting Exposure",
    ),
    "docs/STACK_HISTORY.md": (
        "selected, non-exhaustive inventory",
        "not an exhaustive inventory",
        "MS-DOS 6.2 and hands-on experience across Microsoft Windows",
        "including Windows XP x64",
        "Terraform — historical/foundational exposure",
        "Ansible — historical professional automation experience",
    ),
}
PROHIBITED_PROFILE_CLAIMS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "unsupported percentage claim",
        re.compile(r"\b95\s*%\+?", re.IGNORECASE),
    ),
    (
        "stale relative-date label",
        re.compile(r"\b(?:recent|latest update|last updated)\s*:", re.IGNORECASE),
    ),
    (
        "removed private-project reference",
        re.compile(r"\b(?:PortalSDK|tags-mcp(?:-servers)?)\b", re.IGNORECASE),
    ),
    (
        "retired public email",
        re.compile(
            r"\b(?:creesey@wgu\.edu|reesey275@theangrygamershow\.com)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "unapproved professional identity or seniority label",
        re.compile(
            r"\b(?:veteran software engineer|systems architect|senior-level|"
            r"lead architect|platform lead|automation specialist)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "unsupported readiness or maturity label",
        re.compile(
            r"\b(?:production[- ]ready|production[- ]grade|enterprise[- ]grade)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "unsupported universal architecture claim",
        re.compile(r"\b(?:ISaaS|IaaS)/PaaS/SaaS\b", re.IGNORECASE),
    ),
    (
        "unsupported dependency claim",
        re.compile(r"\bzero[- ]dependency\b", re.IGNORECASE),
    ),
    (
        "unsupported superlative or outcome claim",
        re.compile(
            r"\b(?:pioneered|most reliable|prevents? technical debt|"
            r"global scaling|rapid scaling|scalable foundation)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "unsupported universal enforcement claim",
        re.compile(r"\b(?:across|for) all repositories\b", re.IGNORECASE),
    ),
    (
        "unsupported server, tool, or test total",
        re.compile(r"\b\d+\+?\s+(?:MCP\s+)?(?:servers|tools|tests)\b", re.IGNORECASE),
    ),
    (
        "unsupported DevOnboarder-wide authority claim",
        re.compile(
            r"(?:DevOnboarder[^\n]{0,100}\b(?:foundation|orchestrat\w*)\b|"
            r"\b(?:foundation|orchestrat\w*)\b[^\n]{0,100}DevOnboarder)",
            re.IGNORECASE,
        ),
    ),
    (
        "unsupported NSLS induction rationale",
        re.compile(
            r"\bInducted in recognition of leadership(?: excellence)? and "
            r"academic (?:achievement|excellence)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "unverified military-course title",
        re.compile(r"\bKnowledge Operations Management Course\b", re.IGNORECASE),
    ),
    (
        "overbroad opportunity statement",
        re.compile(r"\bOpen to opportunities\b", re.IGNORECASE),
    ),
    (
        "overstated stack-history completeness",
        re.compile(
            r"\b(?:Complete Stack History|Full technology exposure)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "retired city-level location",
        re.compile(
            r"\b(?:Yulee|Fernandina Beach|Cocoa Beach)\b",
            re.IGNORECASE,
        ),
    ),
)
GITHUB_RESERVED_ROOTS = frozenset(
    {
        "apps",
        "codespaces",
        "collections",
        "events",
        "explore",
        "features",
        "issues",
        "join",
        "login",
        "marketplace",
        "new",
        "notifications",
        "orgs",
        "pulls",
        "search",
        "settings",
        "sponsors",
        "topics",
    }
)

INLINE_LINK_RE = re.compile(
    r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)\n]+))"
)
REFERENCE_DEFINITION_RE = re.compile(
    r"^[ \t]*\[[^\]\n]+\]:[ \t]*(?:<([^>\n]+)>|([^\s\n]+))",
    re.MULTILINE,
)
HTML_ATTRIBUTE_RE = re.compile(
    r"\b(?:href|src)\s*=\s*(?:\"([^\"]+)\"|'([^']+)')",
    re.IGNORECASE,
)
AUTOLINK_RE = re.compile(r"<(https?://[^>\s]+)>")
BARE_URL_RE = re.compile(r"https?://[^\s<>\")\]]+")
REPOSITORY_COUNT_RE = re.compile(
    r"\b\d+\s+(?:(?:active|public|private|development)\s+){0,4}"
    r"(?:repos|repositories)\b",
    re.IGNORECASE,
)
GENERATED_WAKA_SECTION_RE = re.compile(
    r"<!--START_SECTION:waka-->.*?<!--END_SECTION:waka-->",
    re.DOTALL,
)
SUPERSEDED_PUBLIC_PROFILE_CONTENT: tuple[
    tuple[str, re.Pattern[str]], ...
] = (
    (
        "retired public contact",
        re.compile(
            r"\b(?:creesey@wgu\.edu|chad\.reesey@outlook\.com|"
            r"reesey275@theangrygamershow\.com)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "retired public location",
        re.compile(
            r"\b(?:Yulee|Fernandina Beach|Cocoa Beach)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "superseded public biography",
        re.compile(
            r"\b(?:veteran software engineer|systems architect|"
            r"NSLS-inducted)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "hard-coded public profile count",
        re.compile(
            rf"(?:{REPOSITORY_COUNT_RE.pattern}|"
            r"\bFollowers?\s*:\s*\d+|\bFollowing\s*:\s*\d+)",
            re.IGNORECASE,
        ),
    ),
    (
        "overbroad numeric tenure shorthand",
        re.compile(r"\b25\+\s+years\b", re.IGNORECASE),
    ),
)


@dataclasses.dataclass(frozen=True)
class LinkReference:
    """A Markdown link destination and its source location."""

    source: pathlib.Path
    line: int
    target: str


@dataclasses.dataclass(frozen=True)
class RepositoryResult:
    """The fail-closed result of a GitHub visibility check."""

    status: str
    detail: str


def mask_fenced_code(text: str) -> str:
    """Replace fenced code contents while preserving offsets and line numbers."""

    masked: list[str] = []
    active_fence: str | None = None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        marker = None
        if stripped.startswith("```"):
            marker = "```"
        elif stripped.startswith("~~~"):
            marker = "~~~"

        if active_fence is None and marker is not None:
            active_fence = marker
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            continue

        if active_fence is not None:
            masked.append("".join("\n" if char == "\n" else " " for char in line))
            if stripped.startswith(active_fence):
                active_fence = None
            continue

        masked.append(line)

    return "".join(masked)


def mask_generated_profile_sections(text: str) -> str:
    """Mask generated profile blocks while preserving offsets and line numbers."""

    return GENERATED_WAKA_SECTION_RE.sub(
        lambda match: "".join(
            "\n" if char == "\n" else " " for char in match.group(0)
        ),
        text,
    )


def extract_link_references(source: pathlib.Path, text: str) -> list[LinkReference]:
    """Extract inline, reference-definition, HTML, and autolink targets."""

    searchable = mask_fenced_code(text)
    matches: list[tuple[int, str]] = []
    patterns = (
        (INLINE_LINK_RE, False),
        (REFERENCE_DEFINITION_RE, False),
        (HTML_ATTRIBUTE_RE, False),
        (AUTOLINK_RE, False),
        (BARE_URL_RE, True),
    )
    for pattern, trim_trailing_punctuation in patterns:
        for match in pattern.finditer(searchable):
            groups = match.groups()
            target = (
                next((group for group in groups if group is not None), "")
                if groups
                else match.group(0)
            )
            target = html.unescape(target.strip())
            if trim_trailing_punctuation:
                target = target.rstrip(".,;:")
            if target:
                matches.append((match.start(), target))

    references: list[LinkReference] = []
    seen: set[tuple[int, str]] = set()
    for offset, target in sorted(matches):
        line = text.count("\n", 0, offset) + 1
        key = (line, target)
        if key in seen:
            continue
        seen.add(key)
        references.append(
            LinkReference(
                source=source,
                line=line,
                target=target,
            )
        )
    return references


def discover_markdown_files(
    root: pathlib.Path,
    inputs: Sequence[str],
) -> list[pathlib.Path]:
    """Resolve the configured public profile inputs inside the repository."""

    files: set[pathlib.Path] = set()
    for raw_input in inputs:
        candidate = (root / raw_input).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as error:
            raise ValueError(f"input escapes repository root: {raw_input}") from error

        if candidate.is_file():
            if candidate.suffix.casefold() == ".md":
                files.add(candidate)
            continue
        if candidate.is_dir():
            for path in candidate.rglob("*.md"):
                resolved_path = path.resolve()
                try:
                    resolved_path.relative_to(root)
                except ValueError as error:
                    relative_path = path.relative_to(root)
                    raise ValueError(
                        "discovered Markdown file escapes repository root: "
                        f"{relative_path}"
                    ) from error
                files.add(resolved_path)
            continue
        raise ValueError(f"profile link input does not exist: {raw_input}")

    return sorted(files)


def read_link_references(files: Iterable[pathlib.Path]) -> list[LinkReference]:
    """Read and extract links from every Markdown input."""

    references: list[LinkReference] = []
    for source in files:
        references.extend(
            extract_link_references(
                source,
                source.read_text(encoding="utf-8"),
            )
        )
    return references


def validate_relative_links(
    root: pathlib.Path,
    references: Iterable[LinkReference],
) -> list[str]:
    """Return errors for missing or repository-escaping relative paths."""

    errors: list[str] = []
    for reference in references:
        try:
            parsed = urllib.parse.urlsplit(reference.target)
        except ValueError as error:
            errors.append(
                f"{reference.source.relative_to(root)}:{reference.line}: "
                f"malformed link target {reference.target!r}: {error}"
            )
            continue

        if parsed.scheme or parsed.netloc or reference.target.startswith("#"):
            continue

        target_path = urllib.parse.unquote(parsed.path)
        if not target_path or target_path.startswith("/"):
            continue

        candidate = (reference.source.parent / target_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(
                f"{reference.source.relative_to(root)}:{reference.line}: "
                f"relative link escapes repository root: {reference.target}"
            )
            continue

        if not candidate.exists():
            errors.append(
                f"{reference.source.relative_to(root)}:{reference.line}: "
                f"relative link target does not exist: {reference.target}"
            )
    return errors


def validate_repository_counts(
    root: pathlib.Path,
    files: Iterable[pathlib.Path],
) -> list[str]:
    """Reject manually maintained numeric repository totals in profile prose."""

    errors: list[str] = []
    for source in files:
        text = source.read_text(encoding="utf-8")
        searchable = mask_fenced_code(mask_generated_profile_sections(text))
        for match in REPOSITORY_COUNT_RE.finditer(searchable):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(
                f"{source.relative_to(root)}:{line}: manually maintained "
                f"repository count is not allowed: {match.group(0)!r}"
            )
    return errors


def validate_profile_claims(
    root: pathlib.Path,
    files: Iterable[pathlib.Path],
) -> list[str]:
    """Reject wording prohibited by the approved public-profile contract."""

    errors: list[str] = []
    for source in files:
        text = source.read_text(encoding="utf-8")
        searchable = mask_fenced_code(mask_generated_profile_sections(text))
        for label, pattern in PROHIBITED_PROFILE_CLAIMS:
            for match in pattern.finditer(searchable):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{source.relative_to(root)}:{line}: {label} is not "
                    f"allowed: {match.group(0)!r}"
                )
    return errors


def validate_superseded_public_profile_content(
    root: pathlib.Path,
) -> list[str]:
    """Reject narrowly scoped superseded claims across all public Markdown."""

    errors: list[str] = []
    files = discover_markdown_files(root, ["."])
    for source in files:
        text = source.read_text(encoding="utf-8")
        searchable = mask_generated_profile_sections(text)
        for label, pattern in SUPERSEDED_PUBLIC_PROFILE_CONTENT:
            for match in pattern.finditer(searchable):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{source.relative_to(root)}:{line}: {label} is not "
                    f"allowed in public Markdown: {match.group(0)!r}"
                )
    return errors


def validate_retired_profile_paths(
    root: pathlib.Path,
    paths: Sequence[str] = RETIRED_PROFILE_PATHS,
) -> list[str]:
    """Require owner-removed profile surfaces to stay absent."""

    errors: list[str] = []
    for relative_path in paths:
        if (root / relative_path).exists():
            errors.append(
                f"retired public-profile path must remain absent: {relative_path}"
            )
    return errors


def validate_required_profile_content(
    root: pathlib.Path,
    requirements: Mapping[str, Sequence[str]] = REQUIRED_PROFILE_SNIPPETS,
) -> list[str]:
    """Require stable owner-approved identity and contact boundaries."""

    errors: list[str] = []
    for relative_path, snippets in requirements.items():
        source = root / relative_path
        if not source.is_file():
            errors.append(f"required public-profile file is missing: {relative_path}")
            continue
        text = source.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                errors.append(
                    f"{relative_path}: required owner-approved wording is "
                    f"missing: {snippet!r}"
                )
    return errors


def required_profile_content_for_files(
    root: pathlib.Path,
    files: Iterable[pathlib.Path],
    requirements: Mapping[str, Sequence[str]] = REQUIRED_PROFILE_SNIPPETS,
) -> dict[str, Sequence[str]]:
    """Return owner-approved content requirements for discovered inputs only."""

    discovered_paths = {
        source.relative_to(root).as_posix()
        for source in files
    }
    return {
        relative_path: snippets
        for relative_path, snippets in requirements.items()
        if relative_path in discovered_paths
    }


def github_repository_name(target: str) -> str | None:
    """Return owner/repository for GitHub repository URLs, not site pages."""

    try:
        parsed = urllib.parse.urlsplit(target)
    except ValueError:
        return None
    if parsed.scheme not in {"http", "https"}:
        return None
    if (parsed.hostname or "").casefold() not in {"github.com", "www.github.com"}:
        return None

    parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
    if len(parts) < 2 or parts[0].casefold() in GITHUB_RESERVED_ROOTS:
        return None

    owner = parts[0]
    repository = parts[1]
    if repository.casefold().endswith(".git"):
        repository = repository[:-4]
    if not owner or not repository:
        return None
    return f"{owner}/{repository}"


def collect_github_repositories(
    references: Iterable[LinkReference],
) -> dict[str, list[LinkReference]]:
    """Group GitHub repository links case-insensitively."""

    grouped: dict[str, list[LinkReference]] = {}
    canonical_names: dict[str, str] = {}
    for reference in references:
        repository = github_repository_name(reference.target)
        if repository is None:
            continue
        key = repository.casefold()
        canonical = canonical_names.setdefault(key, repository)
        grouped.setdefault(canonical, []).append(reference)
    return grouped


def verify_public_repository(
    repository: str,
    *,
    token: str | None,
    attempts: int,
    timeout: float,
    opener: Callable[..., Any] = urllib.request.urlopen,
    sleeper: Callable[[float], None] = time.sleep,
) -> RepositoryResult:
    """Require explicit public visibility, retrying only unverified failures."""

    encoded_repository = urllib.parse.quote(repository, safe="/")
    api_url = f"https://api.github.com/repos/{encoded_repository}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "reesey275-profile-link-policy",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    normalized_token = (token or "").strip()
    if normalized_token:
        headers["Authorization"] = f"Bearer {normalized_token}"

    last_detail = "verification did not run"
    for attempt in range(1, attempts + 1):
        api_request = urllib.request.Request(api_url, headers=headers)
        try:
            with opener(api_request, timeout=timeout) as response:
                status_code = getattr(response, "status", response.getcode())
                body = response.read()
        except urllib.error.HTTPError as error:
            if error.code in {404, 410}:
                return RepositoryResult(
                    "inaccessible",
                    f"GitHub returned HTTP {error.code}",
                )
            last_detail = f"GitHub returned HTTP {error.code}"
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_detail = f"network verification failed: {error}"
        else:
            if status_code != 200:
                last_detail = f"GitHub returned HTTP {status_code}"
            else:
                try:
                    payload = json.loads(body.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError) as error:
                    last_detail = f"GitHub returned an invalid response: {error}"
                else:
                    if not isinstance(payload, dict):
                        last_detail = "GitHub returned an unexpected response shape"
                    elif (
                        payload.get("private") is False
                        and payload.get("visibility") == "public"
                    ):
                        return RepositoryResult(
                            "public",
                            "GitHub explicitly reports public visibility",
                        )
                    elif payload.get("private") is True or payload.get(
                        "visibility"
                    ) in {"private", "internal"}:
                        return RepositoryResult(
                            "non-public",
                            "GitHub explicitly reports non-public visibility",
                        )
                    else:
                        return RepositoryResult(
                            "unverified",
                            "GitHub did not explicitly report public visibility",
                        )

        if attempt < attempts:
            sleeper(float(attempt))

    return RepositoryResult("unverified", last_detail)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        default=list(DEFAULT_INPUTS),
        help="Markdown file or directory paths relative to --root",
    )
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help="repository root (default: current directory)",
    )
    parser.add_argument(
        "--attempts",
        type=int,
        default=3,
        help="maximum GitHub API attempts for an unverified response",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="timeout in seconds for each GitHub API attempt",
    )
    parser.add_argument(
        "--skip-github",
        action="store_true",
        help="validate relative links without making GitHub API requests",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the profile link policy checks."""

    args = build_parser().parse_args(argv)
    if args.attempts < 1:
        raise SystemExit("--attempts must be at least 1")
    if args.timeout <= 0:
        raise SystemExit("--timeout must be greater than 0")

    root = args.root.resolve()
    try:
        files = discover_markdown_files(root, args.paths)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    references = read_link_references(files)
    failures = validate_relative_links(root, references)
    failures.extend(validate_repository_counts(root, files))
    failures.extend(validate_profile_claims(root, files))
    failures.extend(validate_superseded_public_profile_content(root))
    failures.extend(validate_retired_profile_paths(root))
    required_content = required_profile_content_for_files(root, files)
    failures.extend(validate_required_profile_content(root, required_content))

    repositories = collect_github_repositories(references)
    if not args.skip_github:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        for repository in sorted(repositories, key=str.casefold):
            result = verify_public_repository(
                repository,
                token=token,
                attempts=args.attempts,
                timeout=args.timeout,
            )
            if result.status == "public":
                print(f"PUBLIC: https://github.com/{repository}")
                continue

            locations = ", ".join(
                f"{reference.source.relative_to(root)}:{reference.line}"
                for reference in repositories[repository]
            )
            if result.status in {"inaccessible", "non-public"}:
                category = "confirmed accessibility failure"
            else:
                category = "verification unavailable; failing closed"
            failures.append(
                f"{locations}: {category} for https://github.com/{repository}: "
                f"{result.detail}"
            )

    for failure in failures:
        print(f"ERROR: {failure}", file=sys.stderr)

    if failures:
        print(
            f"Profile link policy failed with {len(failures)} error(s).",
            file=sys.stderr,
        )
        return 1

    github_note = "skipped" if args.skip_github else f"{len(repositories)} public"
    print(
        f"Profile link policy passed: {len(files)} Markdown files, "
        f"{github_note} GitHub repositories."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
