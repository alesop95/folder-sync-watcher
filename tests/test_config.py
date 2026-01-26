import json
from pathlib import Path

from folder_sync_watcher.config import SyncConfig


def _write_config(tmp_path: Path, patterns: list[str]) -> Path:
    cfg = {
        'folders': {
            'onedrive': 'C:/dummy',
            'google_drive_relative_path': 'dummy',
        },
        'sync_settings': {
            'excluded_patterns': patterns,
        },
        'logging': {
            'level': 'INFO',
            'log_file': 'x.log',
            'retention_days': 1,
        },
    }
    p = tmp_path / 'config.json'
    p.write_text(json.dumps(cfg), encoding='utf-8')
    return p


def test_is_excluded_matches_filename_glob(tmp_path: Path):
    config_path = _write_config(tmp_path, ['~$*'])
    sc = SyncConfig(str(config_path))

    assert sc.is_excluded(str(tmp_path / '~$temp.docx'))


def test_is_excluded_matches_full_path_glob(tmp_path: Path):
    config_path = _write_config(tmp_path, ['**/skip/**'])
    sc = SyncConfig(str(config_path))

    assert sc.is_excluded(str(tmp_path / 'skip' / 'a.txt'))


def test_is_excluded_matches_substring_fallback(tmp_path: Path):
    config_path = _write_config(tmp_path, ['skipme'])
    sc = SyncConfig(str(config_path))

    assert sc.is_excluded(str(tmp_path / 'x_skipme_y.txt'))
