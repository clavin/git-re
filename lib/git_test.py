from textwrap import dedent
import unittest
from unittest.mock import MagicMock

from lib.git import Git, cleanup_stash, STASH_NAME


class CleanupStashTest(unittest.TestCase):
    def test_removes_top_leftover_stash(self):
        """
        Tests the happy path where there is a leftover stash entry at the top of
        the stash stack.
        """
        mock_git = MagicMock()
        mock_git.stash_list.return_value = dedent(f"""\
        stash@{{0}}: {STASH_NAME}
        stash@{{1}}: WIP
        """)
        mock_git.drop_stash.return_value = Git.Result.SUCCESS

        cleanup_stash(mock_git, MagicMock())

        mock_git.stash_list.assert_called_once()
        mock_git.drop_stash.assert_called_once_with("stash@{0}")

    def test_removes_deep_leftover_stash(self):
        """
        Tests the case where there is a leftover stash entry not at the top of
        the stash stack.
        """
        mock_git = MagicMock()
        mock_git.stash_list.return_value = dedent(f"""\
        stash@{{0}}: Better to ask forgiveness than permission
        stash@{{1}}: WIP
        stash@{{2}}: {STASH_NAME}
        stash@{{3}}: We've always done it this way
        """)
        mock_git.drop_stash.return_value = Git.Result.SUCCESS

        cleanup_stash(mock_git, MagicMock())

        mock_git.stash_list.assert_called_once()
        mock_git.drop_stash.assert_called_once_with("stash@{2}")

    def test_no_stash_entries(self):
        """
        Tests the case where there are no stash entries at all.
        """
        mock_git = MagicMock()
        mock_git.stash_list.return_value = ""

        cleanup_stash(mock_git, MagicMock())

        mock_git.stash_list.assert_called_once()
        mock_git.drop_stash.assert_not_called()

    def test_no_entry_in_stash(self):
        """
        Tests the case where there are stash entries, but none created by git-re.
        """
        mock_git = MagicMock()
        mock_git.stash_list.return_value = dedent(f"""\
        stash@{{0}}: Better to ask forgiveness than permission
        stash@{{1}}: WIP
        stash@{{2}}: Another stash
        stash@{{3}}: We've always done it this way
        """)

        cleanup_stash(mock_git, MagicMock())

        mock_git.stash_list.assert_called_once()
        mock_git.drop_stash.assert_not_called()

    def test_dry_run(self):
        """
        Tests the case where the stash list command is run in dry-run mode.
        """
        mock_git = MagicMock()
        mock_git.stash_list.return_value = None

        cleanup_stash(mock_git, MagicMock())

        mock_git.stash_list.assert_called_once()
        mock_git.drop_stash.assert_not_called()

    def test_stash_list_fails(self):
        """
        Tests the case where the stash list command fails.
        """
        mock_git = MagicMock()
        mock_git.stash_list.return_value = "" # Empty stdout on failure

        cleanup_stash(mock_git, MagicMock())

        mock_git.stash_list.assert_called_once()
        mock_git.drop_stash.assert_not_called()

    def test_drop_stash_fails(self):
        """
        Tests the case where dropping the stash entry fails.
        """
        mock_git = MagicMock()
        mock_git.stash_list.return_value = dedent(f"""\
        stash@{{0}}: {STASH_NAME}
        """)
        mock_git.drop_stash.return_value = Git.Result.FAILED

        mock_log = MagicMock()

        cleanup_stash(mock_git, mock_log)

        mock_git.stash_list.assert_called_once()
        mock_git.drop_stash.assert_called_once_with("stash@{0}")
        mock_log.error.assert_called_once() # Should output a warning message

if __name__ == "__main__":
    unittest.main()
