"""Test della risoluzione della radice sorgente.

Coprono i tre casi che la modifica del 2026-09-10 introduce o corregge: la base esplicita che
sostituisce la ricerca per etichetta, la retrocompatibilita' con le configurazioni che
dichiarano solo l'etichetta di volume, e la normalizzazione della lettera nuda, che nel codice
precedente produceva un percorso relativo all'unita' invece che assoluto.
"""

from folder_sync_watcher import source


def _config(**folders):
    base = {'onedrive': 'C:/dummy'}
    base.update(folders)
    return {'folders': base, 'sync_settings': {'ssd_volume_label': 'T7', 'check_ssd_connected': True}}


def test_base_esplicita_vince_sulla_etichetta():
    cfg = _config(source_base='C:\\Users\\tizio\\Cloud\\My files',
                  source_relative_path='Archivio\\Studi')

    assert source.usa_base_esplicita(cfg) is True
    assert source.risolvi_percorso(cfg) == 'C:\\Users\\tizio\\Cloud\\My files\\Archivio\\Studi'


def test_base_esplicita_ignora_lo_stato_dell_ssd(monkeypatch):
    monkeypatch.setattr(source, 'find_ssd_drive_letter', lambda _label: None)
    cfg = _config(source_base='D:\\Base', source_relative_path='x')

    assert source.risolvi_percorso(cfg) == 'D:\\Base\\x'


def test_senza_base_si_cerca_per_etichetta(monkeypatch):
    monkeypatch.setattr(source, 'find_ssd_drive_letter', lambda label: 'J:' if label == 'T7' else None)
    cfg = _config(google_drive_relative_path='googleDrive_sync\\Studi')

    assert source.usa_base_esplicita(cfg) is False
    assert source.risolvi_percorso(cfg) == 'J:\\googleDrive_sync\\Studi'


def test_lettera_nuda_diventa_percorso_assoluto(monkeypatch):
    """Regressione: Path('J:') / rel produce 'J:rel', relativo alla cwd di quell'unita'."""
    monkeypatch.setattr(source, 'find_ssd_drive_letter', lambda _label: 'J:')
    cfg = _config(google_drive_relative_path='a\\b')

    risolto = source.risolvi_percorso(cfg)

    assert risolto == 'J:\\a\\b'
    assert not risolto.startswith('J:a')


def test_ssd_assente_da_percorso_nullo(monkeypatch):
    monkeypatch.setattr(source, 'find_ssd_drive_letter', lambda _label: None)
    cfg = _config(google_drive_relative_path='x')

    assert source.risolvi_percorso(cfg) is None


def test_nome_storico_del_percorso_relativo_resta_valido():
    cfg = _config(source_base='C:\\Base', google_drive_relative_path='storico')

    assert source.percorso_relativo(cfg) == 'storico'


def test_nome_nuovo_ha_precedenza_su_quello_storico():
    cfg = _config(source_base='C:\\Base',
                  source_relative_path='nuovo',
                  google_drive_relative_path='storico')

    assert source.percorso_relativo(cfg) == 'nuovo'


def test_descrizione_attesa_distingue_i_due_casi():
    esplicita = _config(source_base='C:\\Base')
    per_etichetta = _config(google_drive_relative_path='x')

    assert 'C:\\Base' in source.descrizione_attesa(esplicita)
    assert 'T7' in source.descrizione_attesa(per_etichetta)
