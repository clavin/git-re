<center>
<img src="git-re.svg" width="256" height="256" align="center" alt="git-re" />

***git*** script for ***re***vising commits
</center>

`git-re` is a command-line tool that simplifies the process of editing a past Git commit. It automates "***r***ebase-***e***diting" a commit, simplifying the workflow to one or two commands.

## The problem

When you need to edit a specific commit, the basic workflow is:

```shell
# 1. Start an interactive rebase at the commit's parent
$ git rebase -i <commit-hash>^

# 2. Manually change "pick" to "edit" for that commit in the rebase todo
-pick <commit-hash> # target commit
+edit <commit-hash> # target commit
 pick a1b2c3d # next commit
 pick 4e5f678 # next commit

# 3. Make your changes
...

# 4. Stage your changes
$ git add <files>

# 5. Amend the commit
$ git commit --amend --no-edit

# 6. Continue the rebase
$ git rebase --continue
```

This script automates steps 1–2 and 5–6, reducing the process to:

```shell
$ git re <commit-hash>   # rebase-edit mode
  ... make and stage changes ...
$ git re --done          # amends and continues the rebase
```

If you have changes already staged to apply to the commit, the `--stash` flow **does the entire workflow** in one command:

```shell
$ git re --stash <commit-hash>
# stash, rebase, pop, amend, continue
``` 

## Setup

1. Clone this repo
2. Add the `bin` directory to your `PATH` environment variable

```shell
git clone "https://github.com/clavin/git-re.git"
export PATH="$PATH:/path/to/git-re/bin"
```

> [!INFO]
> If you want to make this change permanent, augment `PATH` in your shell's configuration file (e.g., `.bashrc`, `.zshrc`, etc.).

## Usage

`git-re` can be triggered directly, or though git as `git re`.

```shell
$ git re [options] [--stash] <commit-hash>
$ git re [options] --done
$ git re [options] --abort
$ git re --help
```

With no options, `git-re <commit-hash>` will start an interactive rebase at the specified commit. The commit will be marked for editing, and the rebase will be paused at that commit, allowing you to make changes. After making your changes, you can continue the rebase with `git re --done`, or abort it with `git re --abort`.

If you already have staged changes you want to apply to the commit, use `--stash` mode. This will stash your staged changes before starting the rebase, automatically pop the stash, then complete the rebase after you've made your edits.

Conflicts during the rebase must be resolved manually. After resolving conflicts, use `git re --done` to continue.

### Options

The main options are:

* `--stash`, `-s`: **Stash mode.** Stashes *staged* changes before rebase-editing, then automatically pops the stash and completes the rebase-edit.
* `--done`: Completes an in-progress rebase-edit by continuing the rebase.
* `--abort`: Aborts an in-progress rebase-edit.

Additional debugging options:

* `--verbose`, `-v`: Show detailed output.
* `--dry-run`: Do not run mutating commands. Implies `--verbose`.


## Example

```shell
$ cat README | sed 's/the Committee/Grace Hopper/g' > README

$ git re --stash abcd123

$ git show abcd123
```
```diff
commit abcd123
Author: Grace Hopper <admiral@nanosecond.navy.mil>
Date:   Tue Sep 9 1947 15:45:00 -0400

    update attribution

    requested by the committee

    easier to ask forgiveness than to get CI to pass :)

diff --git a/README b/README
index a1b2c3d..4e5f678 100644
--- a/README
+++ b/README
@@ -0,7 +0,7 @@
 COBOL COMPILER
 ==============
-Developed by J. Presper Eckert
+Developed by Grace Hopper

 Overview
 --------
 COBOL is a programming language designed for business.
```
