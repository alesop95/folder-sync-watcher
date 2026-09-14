"""Test del wrapper SUBST.

Il punto da verificare non e' che Windows monti davvero un'unita' (e' un dettaglio del
sistema operativo), ma che il comando parta come lista di argomenti e non come stringa
passata a `cmd.exe` con `shell=True`: un percorso con un'emoji, come quello di Proton sotto
"Ongoing studies", arriva altrimenti troncato dalla codepage legacy della console e SUBST
fallisce senza una ragione visibile in superficie (verificato sul campo il 2026-09-14).
"""

from unittest.mock import patch

from folder_sync_watcher.subst import SubstManager


def _esito(returncode=0):
    class _Esito:
        pass

    e = _Esito()
    e.returncode = returncode
    e.stdout = ''
    return e


def test_create_subst_drive_non_usa_la_shell():
    with patch('subprocess.run', return_value=_esito(0)) as mock_run:
        assert SubstManager.create_subst_drive('A', r'C:\percorso con 🛠️ emoji') is True

    args, kwargs = mock_run.call_args
    assert args[0] == ['subst', 'A:', r'C:\percorso con 🛠️ emoji']
    assert 'shell' not in kwargs or kwargs['shell'] is False


def test_remove_subst_drive_non_usa_la_shell():
    with patch('subprocess.run', return_value=_esito(0)) as mock_run:
        assert SubstManager.remove_subst_drive('A') is True

    args, kwargs = mock_run.call_args
    assert args[0] == ['subst', 'A:', '/D']
    assert 'shell' not in kwargs or kwargs['shell'] is False


def test_create_subst_drive_fallisce_senza_sollevare():
    with patch('subprocess.run', return_value=_esito(1)):
        assert SubstManager.create_subst_drive('A', r'C:\qualunque') is False


def test_create_subst_drive_eccezione_non_si_propaga():
    with patch('subprocess.run', side_effect=OSError('boom')):
        assert SubstManager.create_subst_drive('A', r'C:\qualunque') is False


def test_list_subst_drives_riconosce_il_formato_reale():
    """Regressione: l'output vero di subst.exe e' "A:\\: => percorso", due punti seguiti dal
    backslash prima del separatore, non solo i due punti. Il parser precedente non toglieva
    mai il backslash finale e non riconosceva quindi alcuna unita' gia' montata."""
    esito = _esito(0)
    esito.stdout = 'A:\\: => C:\\Users\\Utente\\Proton Drive\\alesop95\\My files\\x\n'
    with patch('subprocess.run', return_value=esito):
        drives = SubstManager.list_subst_drives()

    assert drives == {'A': r'C:\Users\Utente\Proton Drive\alesop95\My files\x'}


def test_is_subst_drive_vero_dopo_il_parsing_corretto():
    esito = _esito(0)
    esito.stdout = 'A:\\: => C:\\qualunque\n'
    with patch('subprocess.run', return_value=esito):
        assert SubstManager.is_subst_drive('A') is True
        assert SubstManager.is_subst_drive('B') is False
