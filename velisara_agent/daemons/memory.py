from .base import ManagedDaemon
from ..paths import STATE_FILE, SNAPSHOT_FILE
from ..utils import read_json, write_json, now_iso


class MemoryDaemon(ManagedDaemon):
    name = 'memory'

    def tick(self, context):
        state = read_json(STATE_FILE, {})
        snap = {
            'timestamp': now_iso(),
            'state': state,
            'boot_summary': context.get('boot_summary', []),
        }
        write_json(SNAPSHOT_FILE, snap)
        context['logger'].event('debug', 'Memory daemon wrote snapshot.')
