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

    def acquire_lock(self) -> BootStatus:
        if PID_FILE.exists():
            try:
                pid = int(PID_FILE.read_text(encoding='utf-8').strip())
                os.kill(pid, 0)
                return BootStatus('lock', False, [f'Another launcher appears active with PID {pid}.'])
            except Exception:
                pass
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PID_FILE.write_text(str(os.getpid()), encoding='utf-8')
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
            'identity_store': file_nonempty(IDENTITY_FILE),
            'memory_store': file_nonempty(MEMORY_FILE),
            'state_store': file_nonempty(STATE_FILE),
            'config': file_nonempty(CONFIG_FILE),
            'recovery_snapshot': file_nonempty(SNAPSHOT_FILE),
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            return BootStatus('validate', False, [f'Missing or empty: {name}' for name in missing])
        return BootStatus('validate', True, [f'Validated {len(required)} required files.'])

    def write_manifest(self, manifest: Dict) -> BootStatus:
        write_json(MANIFEST_FILE, manifest)
        return BootStatus('manifest', True, ['Body manifest written.'])

    def release_lock(self) -> None:
        try:
            if PID_FILE.exists():
                PID_FILE.unlink()
        except Exception:
            self.logger.boot('warning', 'Failed to remove PID lock cleanly.')
