"""Paths for the maintained package.

Original root-level state files are an archival upload, not live input.
VELISARA_DATA_HOME is used for disposable test roots and explicit user data.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path(
    os.environ.get('VELISARA_DATA_HOME', str(Path.home() / '.velisara_agent'))
).expanduser().resolve()
CONFIG_DIR = DATA_ROOT / 'config'
DATA_DIR = DATA_ROOT / 'data'
LOG_DIR = DATA_ROOT / 'logs'
BACKUP_DIR = DATA_ROOT / 'backups'
ORGANS_DIR = DATA_ROOT / 'organs'
DAEMONS_DIR = DATA_ROOT / 'daemons'
RUNTIME_DIR = DATA_ROOT / 'runtime'

CONFIG_FILE = CONFIG_DIR / 'system_config.json'
IDENTITY_FILE = DATA_DIR / 'identity.json'
MEMORY_FILE = DATA_DIR / 'memory.jsonl'
STATE_FILE = DATA_DIR / 'state.json'
MANIFEST_FILE = DATA_DIR / 'body_manifest.json'
HEARTBEAT_FILE = RUNTIME_DIR / 'heartbeat.json'
PID_FILE = RUNTIME_DIR / 'launcher.pid'
EVENT_LOG = LOG_DIR / 'events.log'
BOOT_LOG = LOG_DIR / 'boot.log'
SNAPSHOT_FILE = BACKUP_DIR / 'last_snapshot.json'

ALL_DIRS = [CONFIG_DIR, DATA_DIR, LOG_DIR, BACKUP_DIR, RUNTIME_DIR, ORGANS_DIR, DAEMONS_DIR]
