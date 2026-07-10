import unittest
import os
import tempfile
import json
from unittest.mock import patch
from src.satya.sdk.adapters.langsmith import LangSmithAdapter
from src.satya.sdk.adapters.file import FileAdapter

class TestAdaptersExtra(unittest.TestCase):
    @patch('src.satya.sdk.adapters.langsmith.requests.post')
    def test_langsmith_adapter(self, mock_post):
        # Set dummy env vars for test
        os.environ['LANGSMITH_API_KEY'] = 'dummy_key'
        adapter = LangSmithAdapter()
        adapter.export_trace('trace-123', 'test_agent', 'prompt', {'prompt': 'hello', 'response': 'world'})

        self.assertTrue(mock_post.called)
        call_args, call_kwargs = mock_post.call_args

        self.assertIn('https://api.smith.langchain.com/runs', call_args[0])
        payload = call_kwargs['json']

        self.assertEqual(payload['run_type'], 'llm')
        self.assertEqual(payload['inputs'], 'hello')
        self.assertEqual(payload['outputs'], 'world')
        self.assertIn('end_time', payload)

        # test invalid uuid fallback
        adapter.export_trace('unknown', 'test_agent', 'prompt', {'prompt': 'hello', 'response': 'world'})
        self.assertTrue(mock_post.called)
        call_args, call_kwargs = mock_post.call_args
        payload = call_kwargs['json']
        self.assertNotEqual(payload['id'], 'unknown')

    def test_file_adapter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "subdir", "traces.jsonl")
            adapter = FileAdapter(filepath)

            adapter.export_trace('trace-123', 'test_agent', 'event', {'data': 'test'})
            adapter.export_log('test_agent', 'hello world', 'task-1')

            self.assertTrue(os.path.exists(filepath))
            with open(filepath, 'r') as f:
                lines = f.readlines()
                self.assertEqual(len(lines), 2)

                trace_data = json.loads(lines[0])
                self.assertEqual(trace_data['trace_id'], 'trace-123')

                log_data = json.loads(lines[1])
                self.assertEqual(log_data['message'], 'hello world')
