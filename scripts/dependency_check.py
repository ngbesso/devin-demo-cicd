#!/usr/bin/env python3
"""Scan requirements.txt for outdated packages and generate a markdown report.

Usage:
    python scripts/dependency_check.py \
        [--requirements REQUIREMENTS_FILE] [--output OUTPUT_FILE]

If --output is not specified, the report is printed to stdout.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class PackageInfo:
    name: str
    installed_version: str
    latest_version: str
    is_outdated: bool


def parse_requirements(requirements_path: Path) -> list[str]:
    """Parse package names from a requirements.txt file."""
    packages: list[str] = []
    for line in requirements_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        # Extract package name (before any version specifier)
        for sep in (">=", "<=", "==", "!=", "~=", ">", "<"):
            if sep in line:
                line = line[: line.index(sep)]
                break
        packages.append(line.strip())
    return packages


def get_outdated_packages() -> dict[str, dict[str, str]]:
    """Get a mapping of outdated package names to their version info."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"Warning: pip list --outdated failed: {result.stderr}", file=sys.stderr)
        return {}

    outdated: dict[str, dict[str, str]] = {}
    for entry in json.loads(result.stdout):
        outdated[entry["name"].lower()] = {
            "installed": entry["version"],
            "latest": entry["latest_version"],
        }
    return outdated


def get_installed_version(package_name: str) -> str:
    """Get the installed version of a package."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", package_name],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return "not installed"
    for line in result.stdout.splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def check_packages(requirements_path: Path) -> list[PackageInfo]:
    """Check all packages in requirements.txt for updates."""
    package_names = parse_requirements(requirements_path)
    outdated = get_outdated_packages()

    results: list[PackageInfo] = []
    for name in package_names:
        normalized = name.lower().replace("-", "-")
        installed = get_installed_version(name)

        if normalized in outdated:
            results.append(
                PackageInfo(
                    name=name,
                    installed_version=outdated[normalized]["installed"],
                    latest_version=outdated[normalized]["latest"],
                    is_outdated=True,
                )
            )
        else:
            # Also check with underscore normalization
            alt_normalized = name.lower().replace("-", "_")
            if alt_normalized in outdated:
                results.append(
                    PackageInfo(
                        name=name,
                        installed_version=outdated[alt_normalized]["installed"],
                        latest_version=outdated[alt_normalized]["latest"],
                        is_outdated=True,
                    )
                )
            else:
                results.append(
                    PackageInfo(
                        name=name,
                        installed_version=installed,
                        latest_version=installed,
                        is_outdated=False,
                    )
                )
    return results


def generate_report(packages: list[PackageInfo], requirements_path: Path) -> str:
    """Generate a markdown report of dependency status."""
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    outdated_count = sum(1 for p in packages if p.is_outdated)
    total_count = len(packages)

    lines: list[str] = [
        "# Dependency Check Report",
        "",
        f"**Generated:** {now}",
        f"**Requirements file:** `{requirements_path}`",
        f"**Total packages:** {total_count}",
        f"**Outdated packages:** {outdated_count}",
        "",
    ]

    if outdated_count == 0:
        lines.append("All dependencies are up to date! :white_check_mark:")
    else:
        lines.append(
            f"**{outdated_count} package(s) have updates available.** "
            "Consider updating them."
        )

    lines.extend(
        [
            "",
            "## Package Status",
            "",
            "| Package | Installed | Latest | Status |",
            "|---------|-----------|--------|--------|",
        ]
    )

    for pkg in sorted(packages, key=lambda p: (not p.is_outdated, p.name.lower())):
        status = "Update available" if pkg.is_outdated else "Up to date"
        icon = ":warning:" if pkg.is_outdated else ":white_check_mark:"
        lines.append(
            f"| {pkg.name} | {pkg.installed_version} | {pkg.latest_version} "
            f"| {icon} {status} |"
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
        ]
    )

    if outdated_count > 0:
        lines.append("### Packages to update")
        lines.append("")
        for pkg in packages:
            if pkg.is_outdated:
                lines.append(
                    f"- **{pkg.name}**: `{pkg.installed_version}` → "
                    f"`{pkg.latest_version}`"
                )
        lines.append("")

    lines.extend(
        [
            "---",
            f"*Report generated by `scripts/dependency_check.py` on {now}*",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check for outdated Python dependencies and generate a report."
    )
    parser.add_argument(
        "--requirements",
        default="requirements.txt",
        help="Path to requirements.txt (default: requirements.txt)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file for the markdown report (default: stdout)",
    )
    args = parser.parse_args()

    requirements_path = Path(args.requirements)
    if not requirements_path.exists():
        print(f"Error: {requirements_path} not found", file=sys.stderr)
        return 1

    packages = check_packages(requirements_path)
    report = generate_report(packages, requirements_path)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report)
        print(f"Report written to {output_path}")
    else:
        print(report)

    # Exit with non-zero status if outdated packages found (useful for CI)
    outdated_count = sum(1 for p in packages if p.is_outdated)
    if outdated_count > 0:
        print(
            f"\n{outdated_count} outdated package(s) found.",
            file=sys.stderr,
        )
        # Return 0 to not fail CI — outdated deps are a warning, not an error
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
