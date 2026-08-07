from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import textwrap
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
GUARD = PROJECT_ROOT / "scripts" / "pr_threads_guard.sh"


class ReviewThreadGuardTests(unittest.TestCase):
    def run_guard(
        self,
        state: str,
        *,
        strict: bool = False,
        ci: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fake_bin = pathlib.Path(temporary_directory)
            fake_gh = fake_bin / "gh"
            fake_gh.write_text(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    set -euo pipefail

                    if [[ "${1:-}" == "repo" && "${2:-}" == "view" ]]; then
                      printf '%s\\n' '{"owner":{"login":"example"},"name":"repo"}'
                      exit 0
                    fi

                    if [[ "${1:-}" == "api" && "${2:-}" == "graphql" ]]; then
                      case "${TEST_THREAD_STATE:?}" in
                        active)
                          resolved=false
                          outdated=false
                          ;;
                        outdated)
                          resolved=false
                          outdated=true
                          ;;
                        resolved)
                          resolved=true
                          outdated=false
                          ;;
                        *)
                          exit 2
                          ;;
                      esac
                      printf '{"data":{"repository":{"pullRequest":{'
                      printf '"title":"Fixture PR","reviewThreads":{'
                      printf '"pageInfo":{"hasNextPage":false,"endCursor":null},'
                      printf '"nodes":[{"id":"THREAD_1","isResolved":%s,' "${resolved}"
                      printf '"isOutdated":%s,"path":"file.md","line":1,' "${outdated}"
                      printf '"comments":{"nodes":[{"author":{"login":"bot"},'
                      printf '"body":"Review concern"}]}}]}}}}}\\n'
                      exit 0
                    fi

                    exit 2
                    """
                ),
                encoding="utf-8",
            )
            fake_gh.chmod(0o755)

            environment = os.environ.copy()
            environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
            environment["TEST_THREAD_STATE"] = state
            if ci:
                environment["CI"] = "true"
            else:
                environment.pop("CI", None)

            command = ["bash", str(GUARD), "123", "--check"]
            if strict:
                command.append("--strict")
            return subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_current_unresolved_feedback_is_actionable(self) -> None:
        result = self.run_guard("active")

        self.assertEqual(result.returncode, 1)
        self.assertIn("ACTIONABLE REVIEW FEEDBACK", result.stdout)

    def test_outdated_unresolved_is_handoff_in_standard_mode(self) -> None:
        result = self.run_guard("outdated")

        self.assertEqual(result.returncode, 0)
        self.assertIn("HUMAN HANDOFF PENDING", result.stdout)
        self.assertIn("STANDARD", result.stdout)

    def test_outdated_unresolved_blocks_in_explicit_strict_mode(self) -> None:
        result = self.run_guard("outdated", strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("HUMAN HANDOFF REQUIRED", result.stdout)
        self.assertIn("not a code or test failure", result.stdout)
        self.assertIn("resolve each thread in the GitHub UI", result.stdout)

    def test_resolved_thread_passes_strict_mode(self) -> None:
        result = self.run_guard("resolved", strict=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("No unresolved review threads", result.stdout)

    def test_ci_environment_does_not_implicitly_select_strict_mode(self) -> None:
        result = self.run_guard("outdated", ci=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("Mode: STANDARD", result.stdout)

    def test_quality_workflow_selects_strict_mode_explicitly(self) -> None:
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "quality.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            '"${{ github.event.pull_request.number }}" --check --strict',
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
