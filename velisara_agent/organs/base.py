from dataclasses import dataclass
from typing import Optional


@dataclass
class OrganStatus:
    name: str
    required: bool
    attached: bool
    message: str
    capability: Optional[str] = None


class Organ:
    name = 'organ'
    required = False
    capability = None

    def attach(self, context) -> OrganStatus:
        raise NotImplementedError
