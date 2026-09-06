import json
import os
import shutil
import time
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + '.bak')


def write_backup(path: Path) -> None:
    if not path.exists() or not path.is_file():
        return
    bak = backup_path(path)
    ensure_parent(bak)
    shutil.copyfile(path, bak)


def restore_from_backup(path: Path) -> bool:
    bak = backup_path(path)
    if not bak.exists() or not bak.is_file():
        return False
    ensure_parent(path)
    shutil.copyfile(bak, path)
    return True


def read_json(path: Path, default: Any) -> Any:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        try:
            bak = backup_path(path)
            with open(bak, 'r', encoding='utf-8') as f:
                data = json.load(f)
            restore_from_backup(path)
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return default
    except OSError:
        return default


def write_json(path: Path, data: Any) -> None:
    ensure_parent(path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    write_backup(path)


def append_jsonl(path: Path, obj: Any) -> None:
    ensure_parent(path)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False) + '\n')
    write_backup(path)


def read_jsonl(path: Path, default: Any) -> Any:
    def _read_lines(src: Path):
        entries = []
        with open(src, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entries.append(json.loads(line))
        return entries

    try:
        return _read_lines(path)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        try:
            data = _read_lines(backup_path(path))
            restore_from_backup(path)
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return default
    except OSError:
        return default


def file_nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def atomic_write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, path)
