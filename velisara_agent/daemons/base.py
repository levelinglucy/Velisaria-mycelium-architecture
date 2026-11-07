"""Background daemon base for the reconstructed package.

The historical flat upload did not include this class. Threads are local,
cooperative and stopped by the launcher; no service or network listener.
"""
import threading


class ManagedDaemon:
    name = 'unnamed'

    def __init__(self, interval_seconds=5):
        if interval_seconds <= 0:
            raise ValueError('interval_seconds must be positive')
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread = None

    def tick(self, context):
        raise NotImplementedError

    def start(self, context):
        if self._thread is not None:
            raise RuntimeError('daemon already started')

        def worker():
            while not self._stop_event.is_set():
                try:
                    self.tick(context)
                except Exception as exc:
                    context['logger'].event(
                        'error', f'{self.name} tick failed: {type(exc).__name__}: {exc}'
                    )
                self._stop_event.wait(self.interval_seconds)

        self._thread = threading.Thread(target=worker, name=f'velisara-{self.name}', daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=3)
