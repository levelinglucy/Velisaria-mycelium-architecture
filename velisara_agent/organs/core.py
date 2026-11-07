from .base import Organ, OrganStatus
from ..paths import IDENTITY_FILE, MEMORY_FILE, EVENT_LOG, SNAPSHOT_FILE
from ..utils import file_nonempty


class IdentityStoreOrgan(Organ):
    name = 'identity_store'
    required = True
    capability = 'identity'

    def attach(self, context):
        ok = file_nonempty(IDENTITY_FILE)
        return OrganStatus(self.name, self.required, ok, 'identity store ready' if ok else 'identity store missing', self.capability)


class MemoryStoreOrgan(Organ):
    name = 'memory_store'
    required = True
    capability = 'memory'

    def attach(self, context):
        ok = file_nonempty(MEMORY_FILE)
        return OrganStatus(self.name, self.required, ok, 'memory journal ready' if ok else 'memory journal missing', self.capability)


class LoggerOrgan(Organ):
    name = 'logger'
    required = True
    capability = 'logging'

    def attach(self, context):
        EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        EVENT_LOG.touch(exist_ok=True)
        return OrganStatus(self.name, self.required, True, 'logger online', self.capability)


class SchedulerOrgan(Organ):
    name = 'scheduler'
    required = True
    capability = 'timing'

    def attach(self, context):
        return OrganStatus(self.name, self.required, True, 'scheduler online', self.capability)


class IOChannelOrgan(Organ):
    name = 'io_channel'
    required = True
    capability = 'stdin/stdout'

    def attach(self, context):
        return OrganStatus(self.name, self.required, True, 'terminal channel attached', self.capability)


class RecoveryManagerOrgan(Organ):
    name = 'recovery_manager'
    required = True
    capability = 'snapshot-recovery'

    def attach(self, context):
        ok = file_nonempty(SNAPSHOT_FILE)
        return OrganStatus(self.name, self.required, ok, 'recovery snapshot available' if ok else 'recovery snapshot unavailable', self.capability)
