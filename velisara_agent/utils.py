"""Minimal local storage helpers.

Valid JSON is written via a same-directory temporary file and replace;
invalid existing JSON is never silently treated as a new empty history.
"""
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any) -> Any:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def write_json(path: Path, data: Any) -> None:
    ensure_parent(path)
    payload = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
    staged = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', encoding='utf-8', dir=path.parent,
            prefix=f'.{path.name}.', suffix='.tmp', delete=False
        ) as f:
            staged = Path(f.name)
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(staged, path)
        staged = None
        # Directory sync may be unsupported (e.g. some mobile filesystems).
        try:
            fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        except OSError:
            pass
    finally:
        if staged is not None:
            try:
                staged.unlink()
            except FileNotFoundError:
                pass


def append_jsonl(path: Path, obj: Any) -> None:
    ensure_parent(path)
    line = json.dumps(obj, ensure_ascii=False) + '\n'
    with open(path, 'a', encoding='utf-8') as f:
        f.write(line)


def validate_jsonl(path: Path) -> None:
    """Read-only check of the maintained JSONL journal before awakening.

    Every line must be a complete UTF-8 JSON object followed by a newline.
    This intentionally scans the whole journal at boot (linear in size)
    rather than extending a possibly interrupted or corrupted record.
    """
    with open(path, 'rb') as handle:
        for number, line in enumerate(handle, 1):
            if not line.endswith(b'\n'):
                raise ValueError(f'Unterminated journal record at line {number}')
            try:
                record = json.loads(line.decode('utf-8'))
            except (UnicodeError, ValueError) as exc:
                raise ValueError(f'Invalid journal record at line {number}') from exc
            if not isinstance(record, dict):
                raise ValueError(f'Non-object journal record at line {number}')


def file_nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0
