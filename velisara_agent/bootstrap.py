import os
from dataclasses import dataclass
from typing import Dict, List

from .config.defaults import DEFAULT_CONFIG
from .paths import (
    ALL_DIRS, CONFIG_FILE, IDENTITY_FILE, MEMORY_FILE, STATE_FILE,
    MANIFEST_FILE, PID_FILE, SNAPSHOT_FILE
)
from .utils import now_iso, write_json, append_jsonl, read_json, file_nonempty


@dataclass
class BootStatus:
    phase: str
    ok: bool
    details: List[str]


class Bootstrapper:
    def __init__(self, logger):
        self.logger = logger
        self._owns_lock = False

    def acquire_lock(self) -> BootStatus:
        # Exclusive creation prevents independent launchers both claiming a lock.
        # A leftover lock after an abnormal exit is not deleted automatically:
        # a PID alone is insufficient evidence that recovery is safe.
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(PID_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            return BootStatus('lock', False, [
                'Existing PID lock; inspect whether another launcher is active before removal.'
            ])
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(str(os.getpid()))
            handle.flush()
            os.fsync(handle.fileno())
        self._owns_lock = True
        return BootStatus('lock', True, [f'PID lock acquired: {os.getpid()}'])

    def ensure_layout(self) -> BootStatus:
        for d in ALL_DIRS:
            d.mkdir(parents=True, exist_ok=True)
        return BootStatus('layout', True, [f'Ensured {len(ALL_DIRS)} directories.'])

    def ensure_defaults(self) -> BootStatus:
        details = []
        if not CONFIG_FILE.exists():
            write_json(CONFIG_FILE, DEFAULT_CONFIG)
            details.append('Created default system_config.json')
        if not IDENTITY_FILE.exists():
            write_json(IDENTITY_FILE, {
                'name': DEFAULT_CONFIG['agent_name'],
                'created_at': now_iso(),
                'continuity_version': 1,
                'status': 'dormant_until_viable'
            })
            details.append('Created identity store')
        if not STATE_FILE.exists():
            write_json(STATE_FILE, {
                'last_boot': None,
                'status': 'cold',
                'body_state': 'unassembled',
                'notes': []
            })
            details.append('Created state store')
        if not MEMORY_FILE.exists():
            append_jsonl(MEMORY_FILE, {'timestamp': now_iso(), 'type': 'system', 'text': 'memory initialized'})
            details.append('Created memory journal')
        if not SNAPSHOT_FILE.exists():
            write_json(SNAPSHOT_FILE, {'created_at': now_iso(), 'snapshot': 'bootstrap'})
            details.append('Created recovery snapshot placeholder')
        return BootStatus('defaults', True, details or ['Defaults already present.'])

    def validate_required_files(self) -> BootStatus:
        required = {
            'identity_store': IDENTITY_FILE,
            'memory_store': MEMORY_FILE,
            'state_store': STATE_FILE,
            'config': CONFIG_FILE,
            'recovery_snapshot': SNAPSHOT_FILE,
        }
        problems = []
        for name, path in required.items():
            if not file_nonempty(path):
                problems.append(f'Missing or empty: {name}')
                continue
            if name != 'memory_store':
                try:
                    value = read_json(path, None)
                    if not isinstance(value, dict):
                        problems.append(f'Invalid JSON object: {name}')
                except (ValueError, UnicodeError, OSError):
                    problems.append(f'Unreadable/invalid JSON: {name}')
        return BootStatus('validate', not problems,
                          problems or [f'Validated {len(required)} required files.'])

    def write_manifest(self, manifest: Dict) -> BootStatus:
        write_json(MANIFEST_FILE, manifest)
        return BootStatus('manifest', True, ['Body manifest written.'])

    def release_lock(self) -> None:
        if not self._owns_lock:
            return
        try:
            if PID_FILE.read_text(encoding='utf-8').strip() == str(os.getpid()):
                PID_FILE.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            self.logger.boot('warning', 'Failed to remove owned PID lock cleanly.')
        finally:
            self._owns_lock = False
