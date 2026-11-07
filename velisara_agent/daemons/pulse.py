from .base import ManagedDaemon
from ..paths import HEARTBEAT_FILE
from ..utils import write_json, now_iso


class PulseDaemon(ManagedDaemon):
    name = 'pulse'

    def tick(self, context):
        write_json(HEARTBEAT_FILE, {
            'timestamp': now_iso(),
            'status': 'alive',
            'agent': context['identity'].get('name', 'unknown'),
        })
        context['logger'].event('debug', 'Pulse heartbeat updated.')
