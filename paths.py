from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_DIR = ROOT / 'config'
DATA_DIR = ROOT / 'data'
LOG_DIR = ROOT / 'logs'
BACKUP_DIR = ROOT / 'backups'
ORGANS_DIR = ROOT / 'organs'
DAEMONS_DIR = ROOT / 'daemons'
RUNTIME_DIR = ROOT / 'runtime'

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
