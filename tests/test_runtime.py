import tempfile
import time
import unittest
from pathlib import Path

import bootstrap
import launcher
from base import ManagedDaemon, OrganStatus


class _Logger:
    def boot(self, _level, _message):
        return None

    def event(self, _level, _message):
        return None


class RuntimeTests(unittest.TestCase):
    def _patch(self, module, **values):
        original = {}
        for key, value in values.items():
            original[key] = getattr(module, key)
            setattr(module, key, value)
        self.addCleanup(lambda: [setattr(module, key, original[key]) for key in values])

    def test_bootstrap_validate_required_files_recovers_from_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / 'config' / 'system_config.json'
            identity = root / 'data' / 'identity.json'
            memory = root / 'data' / 'memory.jsonl'
            state = root / 'data' / 'state.json'
            manifest = root / 'data' / 'body_manifest.json'
            pid = root / 'runtime' / 'launcher.pid'
            snapshot = root / 'backups' / 'last_snapshot.json'
            all_dirs = [root / 'config', root / 'data', root / 'logs', root / 'backups', root / 'runtime']

            self._patch(
                bootstrap,
                CONFIG_FILE=config,
                IDENTITY_FILE=identity,
                MEMORY_FILE=memory,
                STATE_FILE=state,
                MANIFEST_FILE=manifest,
                PID_FILE=pid,
                SNAPSHOT_FILE=snapshot,
                ALL_DIRS=all_dirs,
            )

            boot = bootstrap.Bootstrapper(_Logger())
            boot.ensure_layout()
            boot.ensure_defaults()

            identity.write_text('{broken', encoding='utf-8')
            identity.with_suffix('.json.bak').write_text('{"name":"Recovered"}', encoding='utf-8')
            memory.write_text('not-jsonl\n', encoding='utf-8')
            memory.with_suffix('.jsonl.bak').write_text('{"ok": true}\n', encoding='utf-8')

            status = boot.validate_required_files()
            self.assertTrue(status.ok)
            self.assertIn('Validated', status.details[0])

    def test_assemble_body_reports_non_viable_missing_required(self):
        class RequiredMissing:
            def attach(self, _context):
                return OrganStatus('identity_store', True, False, 'missing', 'identity')

        class OptionalPresent:
            def attach(self, _context):
                return OrganStatus('dream_engine', False, True, 'ok', 'dreaming')

        original = launcher.ALL_ORGANS
        launcher.ALL_ORGANS = [RequiredMissing(), OptionalPresent()]
        self.addCleanup(lambda: setattr(launcher, 'ALL_ORGANS', original))

        config, manifest = launcher.assemble_body(_Logger())
        self.assertIn('minimum_required_organs', config)
        self.assertFalse(manifest['viable'])
        self.assertIn('identity_store', manifest['missing_required'])

    def test_managed_daemon_start_tick_stop(self):
        class CounterDaemon(ManagedDaemon):
            name = 'counter'

            def __init__(self):
                super().__init__(interval_seconds=1)
                self.ticks = 0

            def tick(self, _context):
                self.ticks += 1
                self._running.clear()

        daemon = CounterDaemon()
        daemon.start({'logger': _Logger()})
        time.sleep(0.05)
        self.assertGreaterEqual(daemon.ticks, 1)
        daemon.stop()
        self.assertFalse(daemon.is_running)


if __name__ == '__main__':
    unittest.main()
