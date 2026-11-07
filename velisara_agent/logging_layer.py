from pathlib import Path
from .utils import now_iso, ensure_parent


class EventLogger:
    def __init__(self, event_log: Path, boot_log: Path):
        self.event_log = event_log
        self.boot_log = boot_log
        ensure_parent(event_log)
        ensure_parent(boot_log)

    def _write(self, path: Path, level: str, message: str) -> None:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f'[{now_iso()}] {level.upper()}: {message}\n')

    def event(self, level: str, message: str) -> None:
        self._write(self.event_log, level, message)

    def boot(self, level: str, message: str) -> None:
        self._write(self.boot_log, level, message)
