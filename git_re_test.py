import unittest
from unittest.mock import MagicMock, patch

from lib.git import Git

from git_re import main, _abort_flow, _done_flow, _edit_flow


class MainTest(unittest.TestCase):
    """Tests for the main() function argument validation and flow dispatch."""

    @patch("git_re.Git")
    @patch("git_re.Log")
    @patch("git_re.parse_args")
    def test_abort_with_commit_errors(self, mock_parse_args, mock_log_cls, mock_git_cls):
        """
        Tests that --abort with a commit argument produces an error.
        """
        mock_args = MagicMock(abort=True, done=False, commit="abc123", stash=False)
        mock_parse_args.return_value = mock_args
        mock_log = mock_log_cls.return_value

        result = main()

        self.assertEqual(result, 1)
        mock_log.error.assert_called_once()
        self.assertIn("--abort", mock_log.error.call_args[0][0])
        self.assertIn("commit", mock_log.error.call_args[0][0])

    @patch("git_re.Git")
    @patch("git_re.Log")
    @patch("git_re.parse_args")
    def test_abort_with_stash_errors(self, mock_parse_args, mock_log_cls, mock_git_cls):
        """
        Tests that --abort with --stash produces an error.
        """
        mock_args = MagicMock(abort=True, done=False, commit=None, stash=True)
        mock_parse_args.return_value = mock_args
        mock_log = mock_log_cls.return_value

        result = main()

        self.assertEqual(result, 1)
        mock_log.error.assert_called_once()
        self.assertIn("--abort", mock_log.error.call_args[0][0])
        self.assertIn("--stash", mock_log.error.call_args[0][0])

    @patch("git_re.Git")
    @patch("git_re.Log")
    @patch("git_re.parse_args")
    def test_abort_with_done_errors(self, mock_parse_args, mock_log_cls, mock_git_cls):
        """
        Tests that --abort with --done produces an error.
        """
        mock_args = MagicMock(abort=True, done=True, commit=None, stash=False)
        mock_parse_args.return_value = mock_args
        mock_log = mock_log_cls.return_value

        result = main()

        self.assertEqual(result, 1)
        mock_log.error.assert_called_once()
        self.assertIn("--abort", mock_log.error.call_args[0][0])
        self.assertIn("--done", mock_log.error.call_args[0][0])

    @patch("git_re.Git")
    @patch("git_re.Log")
    @patch("git_re.parse_args")
    def test_done_with_commit_errors(self, mock_parse_args, mock_log_cls, mock_git_cls):
        """
        Tests that --done with a commit argument produces an error.
        """
        mock_args = MagicMock(abort=False, done=True, commit="abc123", stash=False)
        mock_parse_args.return_value = mock_args
        mock_log = mock_log_cls.return_value

        result = main()

        self.assertEqual(result, 1)
        mock_log.error.assert_called_once()
        self.assertIn("--done", mock_log.error.call_args[0][0])
        self.assertIn("commit", mock_log.error.call_args[0][0])

    @patch("git_re.Git")
    @patch("git_re.Log")
    @patch("git_re.parse_args")
    def test_done_with_stash_errors(self, mock_parse_args, mock_log_cls, mock_git_cls):
        """
        Tests that --done with --stash produces an error.
        """
        mock_args = MagicMock(abort=False, done=True, commit=None, stash=True)
        mock_parse_args.return_value = mock_args
        mock_log = mock_log_cls.return_value

        result = main()

        self.assertEqual(result, 1)
        mock_log.error.assert_called_once()
        self.assertIn("--done", mock_log.error.call_args[0][0])
        self.assertIn("--stash", mock_log.error.call_args[0][0])

    @patch("git_re._abort_flow")
    @patch("git_re.Git")
    @patch("git_re.Log")
    @patch("git_re.parse_args")
    def test_dispatches_to_abort_flow(
        self, mock_parse_args, mock_log_cls, mock_git_cls, mock_abort_flow
    ):
        """
        Tests that valid --abort dispatches to _abort_flow.
        """
        mock_args = MagicMock(abort=True, done=False, commit=None, stash=False)
        mock_parse_args.return_value = mock_args
        mock_abort_flow.return_value = 0

        result = main()

        self.assertEqual(result, 0)
        mock_abort_flow.assert_called_once_with(
            mock_log_cls.return_value, mock_git_cls.return_value
        )

    @patch("git_re._done_flow")
    @patch("git_re.Git")
    @patch("git_re.Log")
    @patch("git_re.parse_args")
    def test_dispatches_to_done_flow(
        self, mock_parse_args, mock_log_cls, mock_git_cls, mock_done_flow
    ):
        """
        Tests that valid --done dispatches to _done_flow.
        """
        mock_args = MagicMock(abort=False, done=True, commit=None, stash=False)
        mock_parse_args.return_value = mock_args
        mock_done_flow.return_value = 0

        result = main()

        self.assertEqual(result, 0)
        mock_done_flow.assert_called_once_with(
            mock_log_cls.return_value, mock_git_cls.return_value
        )

    @patch("git_re._edit_flow")
    @patch("git_re.Git")
    @patch("git_re.Log")
    @patch("git_re.parse_args")
    def test_dispatches_to_edit_flow(
        self, mock_parse_args, mock_log_cls, mock_git_cls, mock_edit_flow
    ):
        """
        Tests that default invocation dispatches to _edit_flow.
        """
        mock_args = MagicMock(abort=False, done=False, commit="abc123", stash=False)
        mock_parse_args.return_value = mock_args
        mock_edit_flow.return_value = 0

        result = main()

        self.assertEqual(result, 0)
        mock_edit_flow.assert_called_once_with(
            mock_args, mock_log_cls.return_value, mock_git_cls.return_value
        )

    @patch("git_re._edit_flow")
    @patch("git_re.Git")
    @patch("git_re.Log")
    @patch("git_re.parse_args")
    def test_dispatches_to_edit_flow_with_stash(
        self, mock_parse_args, mock_log_cls, mock_git_cls, mock_edit_flow
    ):
        """
        Tests that invocation with --stash dispatches to _edit_flow with stash enabled.
        """
        mock_args = MagicMock(abort=False, done=False, commit="abc123", stash=True)
        mock_parse_args.return_value = mock_args
        mock_edit_flow.return_value = 0

        result = main()

        self.assertEqual(result, 0)
        mock_edit_flow.assert_called_once_with(
            mock_args, mock_log_cls.return_value, mock_git_cls.return_value
        )
        # Verify stash flag is passed through in args
        self.assertTrue(mock_edit_flow.call_args[0][0].stash)


class AbortFlowTest(unittest.TestCase):
    """Tests for the _abort_flow function."""

    def test_success(self):
        """
        Tests the happy path where abort_rebase succeeds.
        """
        mock_git = MagicMock()
        mock_git.abort_rebase.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""
        mock_log = MagicMock()

        result = _abort_flow(mock_log, mock_git)

        self.assertEqual(result, 0)
        mock_git.abort_rebase.assert_called_once()
        mock_log.info.assert_called_once()
        self.assertIn("aborted", mock_log.info.call_args[0][0].lower())

    def test_abort_rebase_fails(self):
        """
        Tests the case where abort_rebase fails.
        """
        mock_git = MagicMock()
        mock_git.abort_rebase.return_value = Git.Result.FAILED
        mock_log = MagicMock()

        result = _abort_flow(mock_log, mock_git)

        self.assertEqual(result, 1)
        mock_git.abort_rebase.assert_called_once()
        mock_log.error.assert_called_once()
        # cleanup_stash should not be called on failure
        mock_git.stash_list.assert_not_called()

    def test_cleanup_stash_called_on_success(self):
        """
        Tests that cleanup_stash is called after successful abort.
        """
        mock_git = MagicMock()
        mock_git.abort_rebase.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""  # No leftover stash
        mock_log = MagicMock()

        _abort_flow(mock_log, mock_git)

        mock_git.stash_list.assert_called_once()


class DoneFlowTest(unittest.TestCase):
    """Tests for the _done_flow function."""

    def test_success(self):
        """
        Tests the happy path where amend and continue succeed.
        """
        mock_git = MagicMock()
        mock_git.amend_commit.return_value = Git.Result.SUCCESS
        mock_git.continue_rebase.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""  # No leftover stash
        mock_log = MagicMock()

        result = _done_flow(mock_log, mock_git)

        self.assertEqual(result, 0)
        mock_git.amend_commit.assert_called_once()
        mock_git.continue_rebase.assert_called_once()
        mock_log.info.assert_called_once()
        self.assertIn("amended", mock_log.info.call_args[0][0].lower())

    def test_amend_commit_fails(self):
        """
        Tests the case where amend_commit fails.
        """
        mock_git = MagicMock()
        mock_git.amend_commit.return_value = Git.Result.FAILED
        mock_log = MagicMock()

        result = _done_flow(mock_log, mock_git)

        self.assertEqual(result, 1)
        mock_git.amend_commit.assert_called_once()
        mock_git.continue_rebase.assert_not_called()
        mock_log.error.assert_called_once()
        self.assertIn("amend", mock_log.error.call_args[0][0].lower())

    def test_continue_rebase_fails(self):
        """
        Tests the case where continue_rebase fails after successful amend.
        """
        mock_git = MagicMock()
        mock_git.amend_commit.return_value = Git.Result.SUCCESS
        mock_git.continue_rebase.return_value = Git.Result.FAILED
        mock_log = MagicMock()

        result = _done_flow(mock_log, mock_git)

        self.assertEqual(result, 1)
        mock_git.amend_commit.assert_called_once()
        mock_git.continue_rebase.assert_called_once()
        # Should log 3 error messages with recovery instructions
        self.assertEqual(mock_log.error.call_count, 3)
        error_messages = [call[0][0] for call in mock_log.error.call_args_list]
        self.assertTrue(any("rebase" in msg.lower() for msg in error_messages))
        self.assertTrue(any("--done" in msg for msg in error_messages))
        self.assertTrue(any("--abort" in msg for msg in error_messages))

    def test_cleanup_stash_called_on_success(self):
        """
        Tests that cleanup_stash is called after successful done flow.
        """
        mock_git = MagicMock()
        mock_git.amend_commit.return_value = Git.Result.SUCCESS
        mock_git.continue_rebase.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""
        mock_log = MagicMock()

        _done_flow(mock_log, mock_git)

        mock_git.stash_list.assert_called_once()


class EditFlowTest(unittest.TestCase):
    """Tests for the _edit_flow function."""

    def test_success_no_stash(self):
        """
        Tests the happy path without stash mode.
        """
        mock_args = MagicMock(stash=False, commit="abc123")
        mock_git = MagicMock()
        mock_git.rebase_edit.return_value = Git.Result.SUCCESS
        mock_log = MagicMock()

        result = _edit_flow(mock_args, mock_log, mock_git)

        self.assertEqual(result, 0)
        mock_git.rebase_edit.assert_called_once_with("abc123")
        mock_log.info.assert_called_once()
        self.assertIn("--done", mock_log.info.call_args[0][0])

    def test_rebase_fails_no_stash(self):
        """
        Tests when rebase_edit fails without stash mode.
        """
        mock_args = MagicMock(stash=False, commit="abc123")
        mock_git = MagicMock()
        mock_git.rebase_edit.return_value = Git.Result.FAILED
        mock_log = MagicMock()

        result = _edit_flow(mock_args, mock_log, mock_git)

        self.assertEqual(result, 1)
        mock_git.rebase_edit.assert_called_once_with("abc123")
        mock_log.error.assert_called_once()
        # Should not attempt stash operations
        mock_git.pop_stash.assert_not_called()

    def test_stash_mode_no_staged_files(self):
        """
        Tests stash mode when there are no staged files.
        """
        mock_args = MagicMock(stash=True, commit="abc123")
        mock_git = MagicMock()
        mock_git.has_staged.return_value = Git.Result.FAILED
        mock_log = MagicMock()

        result = _edit_flow(mock_args, mock_log, mock_git)

        self.assertEqual(result, 1)
        mock_git.has_staged.assert_called_once()
        mock_git.stash_staged.assert_not_called()
        mock_git.rebase_edit.assert_not_called()
        mock_log.error.assert_called_once()
        self.assertIn("staged", mock_log.error.call_args[0][0].lower())

    def test_stash_mode_stash_staged_fails(self):
        """
        Tests stash mode when stash_staged fails.
        """
        mock_args = MagicMock(stash=True, commit="abc123")
        mock_git = MagicMock()
        mock_git.has_staged.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""  # cleanup_stash finds nothing
        mock_git.stash_staged.return_value = Git.Result.FAILED
        mock_log = MagicMock()

        result = _edit_flow(mock_args, mock_log, mock_git)

        self.assertEqual(result, 1)
        mock_git.has_staged.assert_called_once()
        mock_git.stash_staged.assert_called_once()
        mock_git.rebase_edit.assert_not_called()
        mock_log.error.assert_called_once()
        self.assertIn("stash", mock_log.error.call_args[0][0].lower())

    def test_stash_mode_rebase_fails_pop_succeeds(self):
        """
        Tests stash mode when rebase fails but pop_stash succeeds to restore.
        """
        mock_args = MagicMock(stash=True, commit="abc123")
        mock_git = MagicMock()
        mock_git.has_staged.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""
        mock_git.stash_staged.return_value = Git.Result.SUCCESS
        mock_git.rebase_edit.return_value = Git.Result.FAILED
        mock_git.pop_stash.return_value = Git.Result.SUCCESS
        mock_log = MagicMock()

        result = _edit_flow(mock_args, mock_log, mock_git)

        self.assertEqual(result, 1)
        mock_git.rebase_edit.assert_called_once()
        mock_git.pop_stash.assert_called_once()
        mock_log.error.assert_called_once()  # Only the rebase error
        mock_log.debug.assert_called_once()  # Debug message about restoring

    def test_stash_mode_rebase_fails_pop_fails(self):
        """
        Tests stash mode when rebase fails and pop_stash also fails.
        """
        mock_args = MagicMock(stash=True, commit="abc123")
        mock_git = MagicMock()
        mock_git.has_staged.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""
        mock_git.stash_staged.return_value = Git.Result.SUCCESS
        mock_git.rebase_edit.return_value = Git.Result.FAILED
        mock_git.pop_stash.return_value = Git.Result.FAILED
        mock_log = MagicMock()

        result = _edit_flow(mock_args, mock_log, mock_git)

        self.assertEqual(result, 1)
        mock_git.rebase_edit.assert_called_once()
        mock_git.pop_stash.assert_called_once()
        # Should log rebase error + 2 stash recovery errors
        self.assertEqual(mock_log.error.call_count, 3)
        error_messages = [call[0][0] for call in mock_log.error.call_args_list]
        self.assertTrue(any("rebase" in msg.lower() for msg in error_messages))
        self.assertTrue(any("stash" in msg.lower() for msg in error_messages))

    def test_stash_mode_rebase_succeeds_pop_fails(self):
        """
        Tests stash mode when rebase succeeds but pop_stash fails.
        """
        mock_args = MagicMock(stash=True, commit="abc123")
        mock_git = MagicMock()
        mock_git.has_staged.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""
        mock_git.stash_staged.return_value = Git.Result.SUCCESS
        mock_git.rebase_edit.return_value = Git.Result.SUCCESS
        mock_git.pop_stash.return_value = Git.Result.FAILED
        mock_log = MagicMock()

        result = _edit_flow(mock_args, mock_log, mock_git)

        self.assertEqual(result, 1)
        mock_git.rebase_edit.assert_called_once()
        mock_git.pop_stash.assert_called_once()
        # Should log 3 error messages with recovery instructions
        self.assertEqual(mock_log.error.call_count, 3)
        error_messages = [call[0][0] for call in mock_log.error.call_args_list]
        self.assertTrue(any("stash" in msg.lower() for msg in error_messages))
        self.assertTrue(any("--done" in msg for msg in error_messages))
        self.assertTrue(any("--abort" in msg for msg in error_messages))

    @patch("git_re._done_flow")
    def test_stash_mode_full_success(self, mock_done_flow):
        """
        Tests stash mode happy path - all operations succeed, _done_flow is called.
        """
        mock_args = MagicMock(stash=True, commit="abc123")
        mock_git = MagicMock()
        mock_git.has_staged.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""
        mock_git.stash_staged.return_value = Git.Result.SUCCESS
        mock_git.rebase_edit.return_value = Git.Result.SUCCESS
        mock_git.pop_stash.return_value = Git.Result.SUCCESS
        mock_log = MagicMock()
        mock_done_flow.return_value = 0

        result = _edit_flow(mock_args, mock_log, mock_git)

        self.assertEqual(result, 0)
        mock_git.has_staged.assert_called_once()
        mock_git.stash_staged.assert_called_once()
        mock_git.rebase_edit.assert_called_once_with("abc123")
        mock_git.pop_stash.assert_called_once()
        mock_done_flow.assert_called_once_with(mock_log, mock_git)

    @patch("git_re._done_flow")
    def test_stash_mode_done_flow_fails(self, mock_done_flow):
        """
        Tests stash mode when _done_flow returns failure.
        """
        mock_args = MagicMock(stash=True, commit="abc123")
        mock_git = MagicMock()
        mock_git.has_staged.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""
        mock_git.stash_staged.return_value = Git.Result.SUCCESS
        mock_git.rebase_edit.return_value = Git.Result.SUCCESS
        mock_git.pop_stash.return_value = Git.Result.SUCCESS
        mock_log = MagicMock()
        mock_done_flow.return_value = 1

        result = _edit_flow(mock_args, mock_log, mock_git)

        self.assertEqual(result, 1)
        mock_done_flow.assert_called_once_with(mock_log, mock_git)

    def test_stash_mode_cleanup_called_before_stash(self):
        """
        Tests that cleanup_stash is called before stash_staged in stash mode.
        """
        mock_args = MagicMock(stash=True, commit="abc123")
        mock_git = MagicMock()
        mock_git.has_staged.return_value = Git.Result.SUCCESS
        mock_git.stash_list.return_value = ""
        mock_git.stash_staged.return_value = Git.Result.SUCCESS
        mock_git.rebase_edit.return_value = Git.Result.SUCCESS
        mock_git.pop_stash.return_value = Git.Result.SUCCESS
        mock_git.amend_commit.return_value = Git.Result.SUCCESS
        mock_git.continue_rebase.return_value = Git.Result.SUCCESS
        mock_log = MagicMock()

        _edit_flow(mock_args, mock_log, mock_git)

        # Verify stash_list (cleanup) was called before stash_staged
        calls = mock_git.method_calls
        stash_list_idx = next(i for i, c in enumerate(calls) if c[0] == "stash_list")
        stash_staged_idx = next(i for i, c in enumerate(calls) if c[0] == "stash_staged")
        self.assertLess(stash_list_idx, stash_staged_idx)


if __name__ == "__main__":
    unittest.main()
