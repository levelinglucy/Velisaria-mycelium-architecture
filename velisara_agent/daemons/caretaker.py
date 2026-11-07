from .base import ManagedDaemon
from ..paths import ALL_DIRS


class CaretakerDaemon(ManagedDaemon):
    name = 'caretaker'

    def tick(self, context):
        for d in ALL_DIRS:
            d.mkdir(parents=True, exist_ok=True)
        context['logger'].event('debug', 'Caretaker checked directory integrity.')
