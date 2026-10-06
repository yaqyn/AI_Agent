import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import subprocess

from openai.types.chat import ChatCompletionMessage
from call_function import call_function
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file
from main import run_agent


def tool(name, arguments):
    return SimpleNamespace(id="call_1", function=SimpleNamespace(name=name, arguments=arguments))


def response(content=None, calls=None):
    return SimpleNamespace(usage=None, choices=[SimpleNamespace(message=ChatCompletionMessage(
        role="assistant", content=content, tool_calls=calls))])


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        self.root.mkdir()

    def test_write_read_and_execute(self):
        self.assertIn("Successfully", write_file(str(self.root), "sub/test.py", "print('hello')"))
        self.assertEqual(get_file_content(str(self.root), "sub/test.py"), "print('hello')")
        self.assertIn("hello", run_python_file(str(self.root), "sub/test.py"))

    def test_large_output_is_truncated(self):
        write_file(str(self.root), "noisy.py", "print('x' * 20000)")
        output = run_python_file(str(self.root), "noisy.py")
        self.assertIn("[Output truncated]", output)
        self.assertLess(len(output), 10100)

    def test_timeout_returns_tool_error(self):
        write_file(str(self.root), "slow.py", "pass")
        with patch("functions.run_python_file.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("python", 30)):
            self.assertIn("timed out", run_python_file(str(self.root), "slow.py"))

    def test_symlink_escape(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "secret.py").write_text("print('secret')")
        (self.root / "link").symlink_to(outside, target_is_directory=True)
        for result in [get_file_content(str(self.root), "link/secret.py"),
                       write_file(str(self.root), "link/new.txt", "oops"),
                       run_python_file(str(self.root), "link/secret.py")]:
            self.assertIn("outside", result)
        self.assertFalse((outside / "new.txt").exists())

    def test_traversal(self):
        self.assertIn("outside", write_file(str(self.root), "../escape", "oops"))

    def test_invalid_tool_calls_return_errors(self):
        for name, arguments in [("unknown", "{}"), ("write_file", "{"),
                                ("write_file", "[]"), ("write_file", "{}"),
                                ("get_file_content", '{"working_directory":"/"}'),
                                ("run_python_file", '{"file_path":"a.py","args":[1]}')]:
            with self.subTest(name=name, arguments=arguments):
                result = call_function(tool(name, arguments), working_directory=self.root)
                self.assertEqual(result["tool_call_id"], "call_1")
                self.assertTrue(result["content"].startswith("Error:"))

    def test_read_only_blocks_mutations(self):
        for name in ["write_file", "run_python_file"]:
            self.assertIn("disabled", call_function(tool(name, "{}"), read_only=True)["content"])


class AgentTests(unittest.TestCase):
    def test_tool_round_trip_without_usage(self):
        client = Mock()
        client.chat.completions.create.side_effect = [response(calls=[{
            "id": "call_1", "type": "function", "function": {
                "name": "get_files_info", "arguments": "{}"}}]), response("Done")]
        history = []
        self.assertEqual(run_agent(client, "Inspect", read_only=True, messages=history), "Done")
        self.assertEqual(history[3]["role"], "tool")
        tools = client.chat.completions.create.call_args.kwargs["tools"]
        self.assertEqual(len(tools), 2)

    def test_step_limit(self):
        client = Mock()
        client.chat.completions.create.return_value = response(calls=[{
            "id": "call_1", "type": "function", "function": {
                "name": "unknown", "arguments": "{}"}}])
        with self.assertRaisesRegex(RuntimeError, "Maximum steps"):
            run_agent(client, "Loop", max_steps=2)
        self.assertEqual(client.chat.completions.create.call_count, 2)

    def test_empty_response(self):
        client = Mock()
        client.chat.completions.create.return_value = response()
        with self.assertRaisesRegex(RuntimeError, "empty final"):
            run_agent(client, "Test")
