"""
git-re: a command-line tool that simplifies the process of editing a past Git
commit.
"""

import sys

from lib.args import Args, parse_args
from lib.log import Log
from lib.git import Git, cleanup_stash


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
    cleanup_stash(git, log)

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
        
        cleanup_stash(git, log)

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

    cleanup_stash(git, log)

    log.info("Successfully aborted rebase.")
    return 0


def main() -> int:
    args = parse_args()
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
