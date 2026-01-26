from folder_sync_watcher.paths import FilePathManager


def test_sanitize_filename_replaces_invalid_chars():
    assert FilePathManager.sanitize_filename('a<b>:c"d/\\|?*') == 'a_b__c_d________'


def test_sanitize_filename_collapses_spaces_and_commas():
    assert FilePathManager.sanitize_filename('a,   b') == 'a_b'
    assert FilePathManager.sanitize_filename('  a   b  ') == 'a b'
