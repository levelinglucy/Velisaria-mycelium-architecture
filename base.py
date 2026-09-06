from dataclasses import dataclass
from threading import Event, Thread
from time import sleep
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


class ManagedDaemon:
    name = 'daemon'

    def __init__(self, interval_seconds: int = 5):
        try:
            interval = int(interval_seconds)
        except (TypeError, ValueError):
            interval = 5
        self.interval_seconds = max(1, interval)
        self._running = Event()
        self._thread: Optional[Thread] = None

    def start(self, context) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._running.set()
        self._thread = Thread(target=self._loop, args=(context,), name=f'{self.name}_daemon', daemon=True)
        self._thread.start()

    @property
    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive() and self._running.is_set())

    def stop(self) -> None:
        self._running.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

    def _loop(self, context) -> None:
        while self._running.is_set():
            try:
                self.tick(context)
            except Exception as exc:
                logger = context.get('logger')
                if logger:
                    logger.event('error', f'Daemon {self.name} tick failed: {exc}')
            sleep(self.interval_seconds)

    def tick(self, context) -> None:
        raise NotImplementedError
