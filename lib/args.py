import argparse
from typing import Optional


class Args(argparse.Namespace):
    commit: Optional[str]
    done: bool
    abort: bool
    stash: bool
    verbose: bool
    dry_run: bool


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description="Rebase-edit git commits")
    parser.add_argument("commit", nargs="?", help="Commit hash to rebase-edit")
    parser.add_argument(
        "--done", action="store_true", help="Amend current commit and continue rebase"
    )
    parser.add_argument(
        "--abort", action="store_true", help="Abort the rebase operation"
    )
    parser.add_argument(
        "-s",
        "--stash",
        action="store_true",
        help="Stash staged changes, rebase-edit, pop, amend, and continue the rebase",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print additional information during execution",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes",
    )

    return parser.parse_args(namespace=Args())
