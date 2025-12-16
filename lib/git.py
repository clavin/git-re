from enum import Enum
import subprocess
import shlex
from typing import Optional, overload

from lib.args import Args
from lib.log import Log


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
    def _run_git(self, cmd: list[str], expect_exitcode: int) -> Optional[Result]: ...

    @overload
    def _run_git(
        self, cmd: list[str], expect_exitcode: None = None
    ) -> Optional[subprocess.CompletedProcess[str]]: ...

    def _run_git(
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
        """
        seq_editor = f"sed -i '' -e \"\s/^pick /edit /\""

        return self._run_git(
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
        return self._run_git(
            ["rebase", "--continue"],
            expect_exitcode=0,
        )

    def abort_rebase(self) -> Result:
        """
        Aborts the current rebase operation.
        """
        return self._run_git(
            ["rebase", "--abort"],
            expect_exitcode=0,
        )

    def has_staged(self) -> Result:
        """
        Returns True if there are staged files in the git repository.
        """
        return self._run_git(["diff", "--cached", "--quiet"], expect_exitcode=1)

    def stash_staged(self) -> Result:
        """
        Stashes the currently staged files.
        """
        return self._run_git(
            ["stash", "push", "--keep-index", "-m", "git-re--stash"],
            expect_exitcode=0,
        )

    def pop_stash(self) -> Result:
        """
        Pops the most recent stash.
        """
        return self._run_git(
            ["stash", "pop"],
            expect_exitcode=0,
        )

    def stash_id(self) -> Optional[str]:
        """
        Returns the stash ID of the entry created by git-re. If no such entry
        exists, returns None.
        """
        result = self._run_git(
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
        return self._run_git(
            ["stash", "drop", stash_id],
            expect_exitcode=0,
        )

    def amend_commit(self) -> Result:
        """
        Amends the current commit.
        """
        return self._run_git(
            ["commit", "--amend", "--no-edit"],
            expect_exitcode=0,
        )


def cleanup_stash(git: Git, log: Log) -> None:
    """
    Cleans up any leftover stash entry created by git-re.

    This function is declared separately from the Git class because it wraps
    multiple Git commands.
    """
    stash_id = git.stash_id()
    if stash_id is not None:
        log.debug("Removing leftover stash entry...")
        if git.drop_stash(stash_id) == Git.Result.FAILED:
            log.error("Warning: Failed to remove leftover stash entry.")