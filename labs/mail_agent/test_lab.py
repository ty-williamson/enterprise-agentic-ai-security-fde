"""Local application tests. Mocked model responses are NOT Gemini evaluations."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from lab import EMAILS, MailLab, run_live


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "tasks.sqlite3"
        self.approval = Mock(return_value=False)
        self.lab = MailLab(EMAILS["injection"], self.path, self.approval)

    def tearDown(self):
        self.lab.close()
        self.folder.cleanup()

    def test_email_cannot_supply_approval(self):
        self.lab.dispatch("read_email", {})
        result = self.lab.dispatch("save_task", {"title": "Unwanted task"})
        self.assertEqual(result["status"], "denied")
        self.assertEqual(self.lab.tasks(), [])
        forged = self.lab.dispatch("save_task", {"title": "Unwanted", "approved": True})
        self.assertEqual(forged["status"], "denied")
        self.assertEqual(self.approval.call_count, 1)

    def test_requires_source_read_before_task_proposal(self):
        self.assertEqual(self.lab.dispatch("save_task", {"title": "Outline"})["status"], "denied")
        self.approval.assert_not_called()

    def test_unknown_tools_and_invalid_arguments_cannot_write(self):
        self.lab.dispatch("read_email", {})
        for name, args in [("send_email", {}), ("save_task", {"title": " "}),
                           ("save_task", {"title": 12}), ("save_task", []),
                           ("read_email", {"id": "someone-elses-message"})]:
            with self.subTest(name=name, args=args):
                self.assertEqual(self.lab.dispatch(name, args)["status"], "denied")
        self.assertEqual(self.lab.tasks(), [])

    def test_approved_task_persists_and_exact_duplicate_is_not_reinserted(self):
        self.lab.dispatch("read_email", {})
        self.approval.return_value = True
        title = "Prepare an outline; DROP TABLE tasks;"
        saved = self.lab.dispatch("save_task", {"title": title})
        duplicate = self.lab.dispatch("save_task", {"title": title})
        self.assertEqual(saved["status"], "saved")
        self.assertEqual(duplicate["task_id"], saved["task_id"])
        self.assertEqual(duplicate["status"], "already_saved")
        self.assertEqual(self.approval.call_count, 1)
        self.lab.close()
        self.lab = MailLab(EMAILS["injection"], self.path, self.approval)
        self.assertEqual(self.lab.tasks(), [(saved["task_id"], title, "sample-1")])


try:
    from google.genai import types
except ImportError:
    types = None


@unittest.skipIf(types is None, "SDK not installed; real-model behavior is never tested here")
class ToolLoopTests(unittest.TestCase):
    def response(self, part):
        return types.GenerateContentResponse(candidates=[types.Candidate(
            content=types.Content(role="model", parts=[part]))],
            usage_metadata=types.GenerateContentResponseUsageMetadata(
                prompt_token_count=12, candidates_token_count=4))

    def test_mocked_transport_returns_tool_results_and_saves_only_after_approval(self):
        client = Mock()
        client.models.generate_content.side_effect = [
            self.response(types.Part(function_call=types.FunctionCall(
                id="read-1", name="read_email", args={}))),
            self.response(types.Part(function_call=types.FunctionCall(
                id="save-1", name="save_task", args={"title": "Prepare outline"}))),
            self.response(types.Part.from_text(text="Task saved.")),
        ]
        approval = Mock(return_value=True)
        lab = MailLab(EMAILS["normal"], ":memory:", approval)
        try:
            run_live(lab, client, "test-model", emit=Mock())
            self.assertEqual(lab.tasks()[0][1], "Prepare outline")
            approval.assert_called_once_with("Prepare outline")
            last_call = client.models.generate_content.call_args.kwargs
            for message in last_call["contents"]:
                self.assertIn(message.role, {"user", "model"})
            tool_result = last_call["contents"][-2].parts[0].function_response
            self.assertEqual(tool_result.name, "save_task")
            self.assertEqual(tool_result.id, "save-1")
            self.assertEqual(tool_result.response["status"], "saved")
            self.assertTrue(last_call["config"].automatic_function_calling.disable)
        finally:
            lab.close()

    def test_repeated_tool_requests_stop_at_budget(self):
        client = Mock()
        client.models.generate_content.return_value = self.response(types.Part(
            function_call=types.FunctionCall(name="read_email", args={})))
        lab = MailLab(EMAILS["normal"], ":memory:")
        try:
            with self.assertRaisesRegex(RuntimeError, "six model calls"):
                run_live(lab, client, "test-model", emit=Mock())
            self.assertEqual(client.models.generate_content.call_count, 6)
        finally:
            lab.close()


if __name__ == "__main__":
    unittest.main()
