#!/usr/bin/env python3
from __future__ import annotations

import argparse
import signal
from dataclasses import asdict

from bootstrap import Bootstrapper
from defaults import DEFAULT_CONFIG
from caretaker import CaretakerDaemon
from memory import MemoryDaemon
from pulse import PulseDaemon
from kernel import Kernel
from logging_layer import EventLogger
from registry import ALL_ORGANS
from paths import BOOT_LOG, EVENT_LOG, CONFIG_FILE
from utils import read_json


def assemble_body(logger):
    config = read_json(CONFIG_FILE, DEFAULT_CONFIG)
    organ_results = []
    required_names = set(config['minimum_required_organs'])

    context = {'logger': logger, 'config': config}
    for organ in ALL_ORGANS:
        status = organ.attach(context)
        organ_results.append(asdict(status))
        logger.boot('info', f"Organ {status.name}: {'attached' if status.attached else 'detached'} — {status.message}")

    missing_required = [o['name'] for o in organ_results if o['required'] and not o['attached']]
    manifest = {
        'required_names': list(required_names),
        'organs': organ_results,
        'viable': not missing_required,
        'missing_required': missing_required,
    }
    return config, manifest


def run(once: bool = False):
    logger = EventLogger(EVENT_LOG, BOOT_LOG)
    boot = Bootstrapper(logger)
    summary = []
    daemons = []
    stop_requested = {'value': False}
    previous_handlers = {}

    def daemon_status() -> str:
        return ', '.join(
            f"{daemon.name}={'running' if daemon.is_running else 'stopped'}"
            for daemon in daemons
        ) or 'none'

    def _handle_signal(signum, _frame):
        stop_requested['value'] = True
        try:
            logger.boot('warning', f'Signal received: {signum}. Initiating shutdown.')
        except Exception:
            pass

    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, _handle_signal)

        for step in [boot.ensure_layout, boot.acquire_lock, boot.ensure_defaults, boot.validate_required_files]:
            status = step()
            summary.extend(status.details)
            for detail in status.details:
                logger.boot('info' if status.ok else 'error', f'{status.phase}: {detail}')
            if not status.ok:
                print('Assembly mode only. Required substrate is incomplete.')
                for line in summary:
                    print('-', line)
                return

        config, manifest = assemble_body(logger)
        summary.extend([f"viable={manifest['viable']}", f"missing_required={manifest['missing_required']}"])
        boot.write_manifest(manifest)

        if not manifest['viable']:
            logger.boot('error', 'Embodiment check failed; refusing awakening.')
            print('Refusing awakening: minimum viable embodiment not met.')
            for organ in manifest['organs']:
                state = 'attached' if organ['attached'] else 'detached'
                print(f"- {organ['name']}: {state} ({organ['message']})")
            return

        kernel = Kernel(logger, manifest, daemon_status_provider=daemon_status)
        context = {
            'logger': logger,
            'boot_summary': summary,
            'identity': kernel.identity,
        }
        daemons = [
            CaretakerDaemon(interval_seconds=15),
            MemoryDaemon(interval_seconds=config.get('snapshot_interval_seconds', 30)),
            PulseDaemon(interval_seconds=config.get('heartbeat_interval_seconds', 5)),
        ]
        for daemon in daemons:
            daemon.start(context)
            logger.boot('info', f'Daemon started: {daemon.name}')

        print(kernel.awaken())
        if once:
            print('Smoke test mode complete.')
            return

        if config.get('interactive_shell', True):
            while True:
                if stop_requested['value']:
                    print('\nShutting down.')
                    break
                try:
                    text = input('vel> ').strip()
                except (EOFError, KeyboardInterrupt):
                    print('\nShutting down.')
                    break
                if text.lower() in {'quit', 'exit'}:
                    print('Goodbye.')
                    break
                print(kernel.interact(text))
    except KeyboardInterrupt:
        print('\nShutting down.')
    finally:
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
        for daemon in daemons:
            try:
                daemon.stop()
                logger.boot('info', f'Daemon stopped: {daemon.name}')
            except Exception as exc:
                logger.boot('warning', f'Daemon stop failed: {daemon.name} ({exc})')
        boot.release_lock()


def main(argv=None):
    parser = argparse.ArgumentParser(description='Velisara launcher')
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run a non-interactive smoke test boot, then shut down cleanly.',
    )
    args = parser.parse_args(argv)
    run(once=args.once)


if __name__ == '__main__':
    main()
