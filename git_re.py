"""
git-re: a command-line tool that simplifies the process of editing a past Git
commit.
"""

import argparse
from enum import Enum
import shlex
import subprocess
import sys
from typing import Optional, overload


class Args(argparse.Namespace):
    commit: Optional[str]
    done: bool
    abort: bool
    stash: bool
    verbose: bool
    dry_run: bool


class Log:
    """
    Simple "print" wrapper.

    Supports info, error, and debug messages. Debug messages are only printed if
    verbose mode is enabled.
    """

    def __init__(self, args: Args) -> "Log":
        self.verbose = args.verbose or args.dry_run

    def info(self, *args, **kwds):
        """Informational message."""
        print(*args, **kwds)

    def error(self, *args, **kwds):
        """Error message."""
        print(*args, file=sys.stderr, **kwds)

    def debug(self, *args, **kwds):
        """Debug message. Only printed if verbose mode is enabled."""
        if self.verbose:
            print(*args, **kwds)


class Git:
    """
    Wrapper for running git commands.

    If dry-run mode is enabled, commands are only logged and not executed, and
    methods return None.
    """

    class Result(Enum):
        FAILED = 0
        SUCCESS = 1
        DRY_RUN = 2

    def __init__(self, args: Args, log: Log) -> "Git":
        self.dry_run = args.dry_run
        self.log = log

    @overload
    def _exec_git(self, cmd: list[str], expect_exitcode: int) -> Optional[Result]: ...

    @overload
    def _exec_git(
        self, cmd: list[str], expect_exitcode: None = None
    ) -> Optional[subprocess.CompletedProcess[str]]: ...

    def _exec_git(
        self, cmd: list[str], expect_exitcode: Optional[int] = None
    ) -> Optional[subprocess.CompletedProcess[str] | Result]:
        """
        Executes a git command.

        Logs a debug message of the command prefixed with "> " normally, or "# "
        in dry-run mode.

        If expect_exitcode is provided, returns SUCCESS if the command's exit
        code matches it, or FAILED otherwise.
        """
        full_cmd = ["git"] + cmd

        prefix = "# " if self.dry_run else "> "
        formatted_cmd = " ".join(shlex.quote(part) for part in full_cmd)
        self.log.debug(f"{prefix}{formatted_cmd}")

        if self.dry_run:
            return None

        result: subprocess.CompletedProcess[str] = subprocess.run(
            full_cmd, check=False, capture_output=True, text=True
        )

        if expect_exitcode is not None:
            return (
                Git.Result.SUCCESS
                if result.returncode == expect_exitcode
                else Git.Result.FAILED
            )

        return result

    def rebase_edit(self, commit: str) -> Result:
        """
        Starts an interactive rebase to edit the specified commit, without
        prompting the user to manually edit the todo list. This leaves the
        rebase in a state where the specified commit is ready to be amended.

        Returns SUCCESS if the rebase command was successful.
        """
        seq_editor = f"sed -i '' -e \"\s/^pick /edit /\""

        return self._exec_git(
            [
                "-c",
                f"sequence.editor={seq_editor}",
                "rebase",
                "-i",
                f"{commit}^",
            ],
            expect_exitcode=0,
        )

    def continue_rebase(self) -> Result:
        """
        Continues the current rebase operation.
        """
        return self._exec_git(
            ["rebase", "--continue"],
            expect_exitcode=0,
        )

    def abort_rebase(self) -> Result:
        """
        Aborts the current rebase operation.
        """
        return self._exec_git(
            ["rebase", "--abort"],
            expect_exitcode=0,
        )

    def has_staged(self) -> Result:
        """
        Returns True if there are staged files in the git repository.
        """
        return self._exec_git(["diff", "--cached", "--quiet"], expect_exitcode=1)

    def stash_staged(self) -> Result:
        """
        Stashes the currently staged files.
        """
        return self._exec_git(
            ["stash", "push", "--keep-index", "-m", "git-re--stash"],
            expect_exitcode=0,
        )

    def pop_stash(self) -> Result:
        """
        Pops the most recent stash.
        """
        return self._exec_git(
            ["stash", "pop"],
            expect_exitcode=0,
        )

    def stash_id(self) -> Optional[str]:
        """
        Returns the stash ID of the entry created by git-re. If no such entry
        exists, returns None.
        """
        result = self._exec_git(
            ["stash", "list"],
        )

        if result is None:
            return None

        for line in result.stdout.splitlines():
            if "git-re--stash" in line:
                return line.split(":", 1)[0]

        return None

    def drop_stash(self, stash_id: str) -> Result:
        """
        Drops the specified stash entry.
        """
        return self._exec_git(
            ["stash", "drop", stash_id],
            expect_exitcode=0,
        )

    def amend_commit(self) -> Result:
        """
        Amends the current commit.
        """
        return self._exec_git(
            ["commit", "--amend", "--no-edit"],
            expect_exitcode=0,
        )


def _cleanup_stash(git: Git, log: Log) -> None:
    """
    Cleans up any leftover stash entry created by git-re.
    """
    stash_id = git.stash_id()
    if stash_id is not None:
        log.debug("Removing leftover stash entry...")
        if git.drop_stash(stash_id) == Git.Result.FAILED:
            log.error("Warning: Failed to remove leftover stash entry.")


def _done_flow(log: Log, git: Git) -> int:
    """
    Amends the current commit with staged changes and continues the rebase.
    """
    # Amend the current commit
    if git.amend_commit() == Git.Result.FAILED:
        log.error("Error: Failed to amend the current commit.")
        return 1

    # Continue the rebase
    if git.continue_rebase() == Git.Result.FAILED:
        log.error("Error: Failed to finish rebase.")
        log.error("Error: + Fix any conflicts, then run 'git re --done'.")
        log.error("Error: + To cancel the rebase, run 'git re --abort'.")
        return 1

    # Stash flow: if the stash entry is left over, remove it
    _cleanup_stash(git, log)

    # Success
    log.info("Successfully amended commit and continued rebase.")
    return 0


def _edit_flow(args: Args, log: Log, git: Git) -> int:
    """
    Starts an interactive rebase to edit the specified commit.

    If stash mode is enabled, it also runs extra stash commands and the done flow afterward.
    """
    # Stash mode: push staged changes to stash
    if args.stash:
        if git.has_staged() == Git.Result.FAILED:
            log.error(
                "Error: No staged files. Stage your changes with 'git add' before using --stash."
            )
            return 1

        if git.stash_staged() == Git.Result.FAILED:
            log.error("Error: Failed to stash staged changes.")
            return 1

    # Start interactive rebase
    if git.rebase_edit(args.commit) == Git.Result.FAILED:
        log.error("Error: Failed to start interactive rebase.")

        # Try to restore the stash
        if args.stash:
            log.debug("Restoring stash...")
            if git.pop_stash() == Git.Result.FAILED:
                # If it failed, the least we can do is inform the user
                log.error("Error: + Failed to restore stash after rebase failure.")
                log.error(
                    "Error: + To recover your stashed changes, check 'git stash list'."
                )

        return 1

    # Stash mode: pop stash, continue to done flow
    if args.stash:
        if git.pop_stash() == Git.Result.FAILED:
            log.error(
                "Error: Failed to apply stash to commit. The changes are saved in the stash."
            )
            log.error("Error: + Fix any conflicts, then run 'git re --done'.")
            log.error("Error: + To cancel the rebase, run 'git re --abort'.")
            return 1

        return _done_flow(log, git)

    # Success
    log.info("Rebase-editing. Stage your changes, then run 'git re --done'.")
    return 0


def _abort_flow(log: Log, git: Git) -> int:
    """
    Aborts the current rebase operation.
    """
    if git.abort_rebase() == Git.Result.FAILED:
        log.error("Error: Failed to abort rebase.")
        return 1

    _cleanup_stash(git, log)

    log.info("Successfully aborted rebase.")
    return 0


def main() -> int:
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

    args = parser.parse_args(namespace=Args())
    log = Log(args)
    git = Git(args, log)

    if args.abort:
        if args.commit:
            log.error("Error: --abort cannot be used with a commit argument")
            return 1
        elif args.stash:
            log.error("Error: --abort cannot be used with --stash")
            return 1
        elif args.done:
            log.error("Error: --abort cannot be used with --done")
            return 1

        return _abort_flow(log, git)

    elif args.done:
        if args.commit:
            log.error("Error: --done cannot be used with a commit argument")
            return 1
        elif args.stash:
            log.error("Error: --done cannot be used with --stash")
            return 1
        # elif args.abort: # Handled above

        return _done_flow(log, git)

    else:
        return _edit_flow(args, log, git)


if __name__ == "__main__":
    sys.exit(main())
