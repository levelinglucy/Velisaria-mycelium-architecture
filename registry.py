from .core import (
    IdentityStoreOrgan, MemoryStoreOrgan, LoggerOrgan,
    SchedulerOrgan, IOChannelOrgan, RecoveryManagerOrgan,
)
from .optional import VoiceOrgan, DreamEngineOrgan, VisionOrgan, WorldSensorsOrgan, SymbolicRendererOrgan


ALL_ORGANS = [
    IdentityStoreOrgan(),
    MemoryStoreOrgan(),
    LoggerOrgan(),
    SchedulerOrgan(),
    IOChannelOrgan(),
    RecoveryManagerOrgan(),
    VoiceOrgan(),
    DreamEngineOrgan(),
    VisionOrgan(),
    WorldSensorsOrgan(),
    SymbolicRendererOrgan(),
]
