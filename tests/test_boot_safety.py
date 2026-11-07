"""Regression tests operate only on throwaway directories."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestLaunchSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / 'isolated'
        self.env = os.environ.copy()
        self.env['VELISARA_DATA_HOME'] = str(self.home)

    def launch(self):
        return subprocess.run(
            [sys.executable, 'launcher.py'], cwd=REPO_ROOT,
            env=self.env, input='quit\n', capture_output=True,
            text=True, timeout=15,
        )

    def test_clean_launch_and_private_home(self):
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('is awake', result.stdout)
        self.assertTrue((self.home / 'data' / 'memory.jsonl').is_file())
        self.assertFalse((self.home / 'runtime' / 'launcher.pid').exists())

    def test_corrupt_state_preserved_with_no_new_boot_event(self):
        self.assertEqual(self.launch().returncode, 0)
        state = self.home / 'data' / 'state.json'
        journal = self.home / 'data' / 'memory.jsonl'
        identity = self.home / 'data' / 'identity.json'
        state.write_bytes(b'{truncated')
        before = (state.read_bytes(), identity.read_bytes(), journal.read_bytes())
        result = self.launch()
        self.assertEqual(result.returncode, 0)
        self.assertIn('Assembly mode only', result.stdout)
        self.assertEqual(before, (state.read_bytes(), identity.read_bytes(), journal.read_bytes()))

    def test_corrupt_config_preserved(self):
        self.assertEqual(self.launch().returncode, 0)
        config = self.home / 'config' / 'system_config.json'
        config.write_bytes(b'not-json')
        before = config.read_bytes()
        result = self.launch()
        self.assertIn('Assembly mode only', result.stdout)
        self.assertEqual(config.read_bytes(), before)

    def test_structurally_invalid_config_fails_closed(self):
        self.assertEqual(self.launch().returncode, 0)
        config = self.home / 'config' / 'system_config.json'
        config.write_text('{"interactive_shell": true}', encoding='utf-8')
        before = config.read_bytes()
        result = self.launch()
        self.assertIn('Assembly mode only', result.stdout)
        self.assertEqual(config.read_bytes(), before)

    def test_structurally_invalid_state_fails_closed(self):
        self.assertEqual(self.launch().returncode, 0)
        state = self.home / 'data' / 'state.json'
        state.write_text('{"notes": "not a list"}', encoding='utf-8')
        before = state.read_bytes()
        result = self.launch()
        self.assertIn('Assembly mode only', result.stdout)
        self.assertEqual(state.read_bytes(), before)

    def test_corrupt_snapshot_preserved(self):
        self.assertEqual(self.launch().returncode, 0)
        snapshot = self.home / 'backups' / 'last_snapshot.json'
        snapshot.write_bytes(b'null')
        result = self.launch()
        self.assertIn('Assembly mode only', result.stdout)
        self.assertEqual(snapshot.read_bytes(), b'null')

    def assert_corrupt_journal_refuses_awakening(self, damaged):
        self.assertEqual(self.launch().returncode, 0)
        journal = self.home / 'data' / 'memory.jsonl'
        state = self.home / 'data' / 'state.json'
        identity = self.home / 'data' / 'identity.json'
        journal.write_bytes(damaged(journal.read_bytes()))
        before = (journal.read_bytes(), state.read_bytes(), identity.read_bytes())
        result = self.launch()
        self.assertIn('Assembly mode only', result.stdout, result.stderr)
        self.assertNotIn('is awake', result.stdout)
        self.assertEqual(before, (journal.read_bytes(), state.read_bytes(), identity.read_bytes()))

    def test_partial_last_journal_record_is_not_extended(self):
        self.assert_corrupt_journal_refuses_awakening(lambda raw: raw + b'{"partial":')

    def test_valid_but_unterminated_journal_line_is_not_extended(self):
        self.assert_corrupt_journal_refuses_awakening(lambda raw: raw.rstrip(b'\n'))

    def test_invalid_journal_line_is_not_ignored(self):
        self.assert_corrupt_journal_refuses_awakening(lambda raw: raw + b'not-json\n')

    def test_invalid_journal_utf8_is_not_ignored(self):
        self.assert_corrupt_journal_refuses_awakening(lambda raw: raw + b'\xff\n')

    def test_atomic_write_refuses_unserializable_input(self):
        from velisara_agent.utils import write_json
        target = Path(self.temp.name) / 'important.json'
        target.write_bytes(b'{"history":[1]}')
        with self.assertRaises(TypeError):
            write_json(target, {'bad': set([1])})
        self.assertEqual(target.read_bytes(), b'{"history":[1]}')

    def test_foreign_lock_never_removed(self):
        from velisara_agent.bootstrap import Bootstrapper
        from velisara_agent import bootstrap
        lock = Path(self.temp.name) / 'launcher.pid'
        lock.write_text(str(os.getpid()), encoding='utf-8')
        class Dummy:
            def boot(self, *args):
                pass
        with mock.patch.object(bootstrap, 'PID_FILE', lock):
            boot = Bootstrapper(Dummy())
            self.assertFalse(boot.acquire_lock().ok)
            boot.release_lock()
        self.assertEqual(lock.read_text(), str(os.getpid()))

    def test_owned_lock_lifecycle(self):
        from velisara_agent.bootstrap import Bootstrapper
        from velisara_agent import bootstrap
        lock = Path(self.temp.name) / 'launcher.pid'
        class Dummy:
            def boot(self, *args):
                pass
        with mock.patch.object(bootstrap, 'PID_FILE', lock):
            boot = Bootstrapper(Dummy())
            self.assertTrue(boot.acquire_lock().ok)
            self.assertTrue(lock.exists())
            boot.release_lock()
        self.assertFalse(lock.exists())


if __name__ == '__main__':
    unittest.main()
