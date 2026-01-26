from pathlib import Path

from folder_sync_watcher.hashing import FileHasher


def test_get_file_hash_is_stable(tmp_path: Path):
    p = tmp_path / 'a.txt'
    p.write_text('hello', encoding='utf-8')

    h1 = FileHasher.get_file_hash(str(p))
    h2 = FileHasher.get_file_hash(str(p))

    assert h1
    assert h1 == h2


def test_get_file_hash_changes_on_content_change(tmp_path: Path):
    p = tmp_path / 'a.txt'
    p.write_text('hello', encoding='utf-8')
    h1 = FileHasher.get_file_hash(str(p))

    p.write_text('hello2', encoding='utf-8')
    h2 = FileHasher.get_file_hash(str(p))

    assert h1 != h2
