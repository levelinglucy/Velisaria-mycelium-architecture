from .base import Organ, OrganStatus


class VoiceOrgan(Organ):
    name = 'voice'
    required = False
    capability = 'speech'

    def attach(self, context):
        return OrganStatus(self.name, self.required, False, 'voice not yet implemented; safe to run silent', self.capability)


class DreamEngineOrgan(Organ):
    name = 'dream_engine'
    required = False
    capability = 'dreaming'

    def attach(self, context):
        return OrganStatus(self.name, self.required, True, 'dream layer attached in minimal mode', self.capability)


class VisionOrgan(Organ):
    name = 'vision'
    required = False
    capability = 'vision'

    def attach(self, context):
        return OrganStatus(self.name, self.required, False, 'vision detached', self.capability)


class WorldSensorsOrgan(Organ):
    name = 'world_sensors'
    required = False
    capability = 'sensors'

    def attach(self, context):
        return OrganStatus(self.name, self.required, False, 'world sensors detached', self.capability)


class SymbolicRendererOrgan(Organ):
    name = 'symbolic_renderer'
    required = False
    capability = 'symbolics'

    def attach(self, context):
        return OrganStatus(self.name, self.required, True, 'symbolic renderer attached', self.capability)
