#!/usr/bin/env python3
"""Generate repository-hosted GitHub profile statistics cards."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import html
import json
import os
import pathlib
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"
USER_AGENT = "reesey275-profile-stats-generator"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

THEME = {
    "background": "#151515",
    "border": "#e4e2e2",
    "title": "#ffffff",
    "text": "#c9d1d9",
    "muted": "#8b949e",
    "accent": "#79c0ff",
    "track": "#30363d",
}

LANGUAGE_COLORS = {
    "CSS": "#563d7c",
    "Dockerfile": "#384d54",
    "HTML": "#e34c26",
    "JavaScript": "#f1e05a",
    "Makefile": "#427819",
    "PowerShell": "#012456",
    "Python": "#3572a5",
    "Shell": "#89e051",
}


class GitHubAPIError(RuntimeError):
    """Raised when GitHub API data cannot be retrieved safely."""


class GitHubClient:
    """Small GitHub REST client with bounded retries."""

    def __init__(self, token: str | None = None, timeout: int = 30) -> None:
        self.token = token
        self.timeout = timeout

    def get(self, path: str, params: dict[str, str | int] | None = None) -> Any:
        query = urllib.parse.urlencode(params or {})
        url = f"{API_ROOT}{path}"
        if query:
            url = f"{url}?{query}"

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": API_VERSION,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        for attempt in range(3):
            request = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return json.load(response)
            except urllib.error.HTTPError as error:
                body = error.read().decode("utf-8", errors="replace")
                if error.code in RETRYABLE_STATUS_CODES and attempt < 2:
                    time.sleep(2**attempt)
                    continue
                raise GitHubAPIError(
                    f"GitHub API request failed ({error.code}) for {url}: {body}"
                ) from error
            except urllib.error.URLError as error:
                if attempt < 2:
                    time.sleep(2**attempt)
                    continue
                raise GitHubAPIError(
                    f"GitHub API request failed for {url}: {error.reason}"
                ) from error

        raise GitHubAPIError(f"GitHub API request exhausted retries for {url}")


def escaped_path(value: str) -> str:
    """Escape one GitHub API path component."""

    return urllib.parse.quote(value, safe="")


def fetch_owned_repositories(client: GitHubClient, username: str) -> list[dict[str, Any]]:
    """Return every public repository owned by a user."""

    repositories: list[dict[str, Any]] = []
    encoded_username = escaped_path(username)

    for page in range(1, 11):
        batch = client.get(
            f"/users/{encoded_username}/repos",
            {
                "page": page,
                "per_page": 100,
                "sort": "updated",
                "type": "owner",
            },
        )
        if not isinstance(batch, list):
            raise GitHubAPIError("GitHub repositories response was not a list")
        repositories.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise GitHubAPIError("Repository pagination exceeded the safety limit")

    return repositories


def search_total(client: GitHubClient, endpoint: str, query: str) -> int:
    """Return a GitHub search result count."""

    response = client.get(endpoint, {"per_page": 1, "q": query})
    try:
        return int(response["total_count"])
    except (KeyError, TypeError, ValueError) as error:
        raise GitHubAPIError(f"Search response did not include total_count: {query}") from error


def collect_profile_data(
    client: GitHubClient,
    username: str,
    year: int,
) -> tuple[dict[str, int | str], collections.Counter[str]]:
    """Collect the public data used by both profile cards."""

    encoded_username = escaped_path(username)
    user = client.get(f"/users/{encoded_username}")
    repositories = fetch_owned_repositories(client, username)
    source_repositories = [repository for repository in repositories if not repository.get("fork")]

    language_bytes: collections.Counter[str] = collections.Counter()
    for repository in source_repositories:
        full_name = str(repository["full_name"])
        owner, name = full_name.split("/", 1)
        languages = client.get(
            f"/repos/{escaped_path(owner)}/{escaped_path(name)}/languages"
        )
        if not isinstance(languages, dict):
            raise GitHubAPIError(f"Languages response was not an object: {full_name}")
        language_bytes.update(
            {
                str(language): int(byte_count)
                for language, byte_count in languages.items()
            }
        )

    stats: dict[str, int | str] = {
        "commits": search_total(
            client,
            "/search/commits",
            f"author:{username} committer-date:>={year}-01-01",
        ),
        "followers": int(user.get("followers", 0)),
        "issues": search_total(
            client,
            "/search/issues",
            f"author:{username} type:issue",
        ),
        "name": str(user.get("name") or username),
        "public_repositories": int(user.get("public_repos", len(repositories))),
        "pull_requests": search_total(
            client,
            "/search/issues",
            f"author:{username} type:pr",
        ),
        "stars": sum(int(repository.get("stargazers_count", 0)) for repository in source_repositories),
        "username": username,
        "year": year,
    }
    return stats, language_bytes


def svg_text(value: object) -> str:
    """Escape text for safe use inside SVG markup."""

    return html.escape(str(value), quote=True)


def svg_document(width: int, height: int, title: str, body: str) -> str:
    """Wrap card content in a self-contained SVG document."""

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
  viewBox="0 0 {width} {height}" role="img" aria-labelledby="card-title">
  <title id="card-title">{svg_text(title)}</title>
  <style>
    .title {{ fill: {THEME["title"]}; font: 600 18px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .label {{ fill: {THEME["text"]}; font: 400 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .value {{ fill: {THEME["title"]}; font: 600 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .muted {{ fill: {THEME["muted"]}; font: 400 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
  </style>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="6"
    fill="{THEME["background"]}" stroke="{THEME["border"]}"/>
{body}
</svg>
'''


def render_stats_card(stats: dict[str, int | str], updated: str) -> str:
    """Render the GitHub activity summary card."""

    left_column = (
        ("Total Stars Earned", stats["stars"]),
        (f"Public Commits ({stats['year']})", stats["commits"]),
        ("Pull Requests", stats["pull_requests"]),
    )
    right_column = (
        ("Public Repositories", stats["public_repositories"]),
        ("Issues Opened", stats["issues"]),
        ("Followers", stats["followers"]),
    )

    rows: list[str] = []
    for index, (label, value) in enumerate(left_column):
        y = 72 + index * 36
        rows.append(
            f'''  <circle cx="25" cy="{y - 4}" r="4" fill="{THEME["accent"]}"/>
  <text x="39" y="{y}" class="label">{svg_text(label)}</text>
  <text x="226" y="{y}" text-anchor="end" class="value">{svg_text(value)}</text>'''
        )
    for index, (label, value) in enumerate(right_column):
        y = 72 + index * 36
        rows.append(
            f'''  <circle cx="267" cy="{y - 4}" r="4" fill="{THEME["accent"]}"/>
  <text x="281" y="{y}" class="label">{svg_text(label)}</text>
  <text x="470" y="{y}" text-anchor="end" class="value">{svg_text(value)}</text>'''
        )

    display_name = svg_text(stats["name"])
    body = f'''  <text x="25" y="36" class="title">{display_name}'s GitHub Stats</text>
{os.linesep.join(rows)}
  <text x="25" y="198" class="muted">Public GitHub activity • Updated {svg_text(updated)}</text>'''
    return svg_document(495, 215, f"{stats['name']}'s GitHub Stats", body)


def render_languages_card(
    language_bytes: collections.Counter[str],
    updated: str,
    limit: int = 6,
) -> str:
    """Render the top languages card using repository byte counts."""

    total_bytes = sum(language_bytes.values())
    top_languages = language_bytes.most_common(limit)
    if total_bytes <= 0 or not top_languages:
        top_languages = [("No language data", 1)]
        total_bytes = 1

    rows: list[str] = []
    for index, (language, byte_count) in enumerate(top_languages):
        percent = byte_count / total_bytes * 100
        y = 63 + index * 23
        bar_width = max(2.0, 300 * percent / 100)
        color = LANGUAGE_COLORS.get(language, THEME["accent"])
        rows.append(
            f'''  <text x="25" y="{y}" class="label">{svg_text(language)}</text>
  <text x="325" y="{y}" text-anchor="end" class="value">{percent:.1f}%</text>
  <rect x="25" y="{y + 7}" width="300" height="5" rx="2.5" fill="{THEME["track"]}"/>
  <rect x="25" y="{y + 7}" width="{bar_width:.1f}" height="5" rx="2.5" fill="{color}"/>'''
        )

    body = f'''  <text x="25" y="36" class="title">Top Languages</text>
{os.linesep.join(rows)}
  <text x="25" y="198" class="muted">Public, non-fork repositories • Updated {svg_text(updated)}</text>'''
    return svg_document(350, 215, "Top Languages", body)


def write_atomic(path: pathlib.Path, content: str) -> None:
    """Replace an output file only after its full content is available."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        newline="\n",
    ) as handle:
        handle.write(content)
        temporary_path = pathlib.Path(handle.name)
    temporary_path.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--username",
        default=os.environ.get("GITHUB_REPOSITORY_OWNER", "reesey275"),
        help="GitHub username to summarize",
    )
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=pathlib.Path("profile"),
        help="Directory for generated SVG files",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=dt.datetime.now(dt.timezone.utc).year,
        help="UTC year used for the public commit count",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    client = GitHubClient(token=token)
    stats, language_bytes = collect_profile_data(client, args.username, args.year)
    updated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d UTC")

    stats_path = args.output_dir / "github-stats.svg"
    languages_path = args.output_dir / "top-languages.svg"
    write_atomic(stats_path, render_stats_card(stats, updated))
    write_atomic(languages_path, render_languages_card(language_bytes, updated))

    print(
        json.dumps(
            {
                "languages": [name for name, _ in language_bytes.most_common(6)],
                "output": [str(stats_path), str(languages_path)],
                "stats": stats,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
