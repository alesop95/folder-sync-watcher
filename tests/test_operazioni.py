"""Test del punto unico di scrittura e della prova a vuoto.

La prova che conta non e' che i metodi restituiscano il valore giusto, ma che in prova a vuoto
il filesystem resti identico a prima: e' quello il motivo per cui la modalita' esiste, ed e'
l'unica affermazione che vale la pena verificare in modo diretto.
"""

import logging
import stat

from folder_sync_watcher.operazioni import OperazioniFile


def _operazioni(prova_a_vuoto):
    logger = logging.getLogger('test_operazioni')
    logger.addHandler(logging.NullHandler())
    return OperazioniFile(logger, prova_a_vuoto=prova_a_vuoto)


def test_modalita_reale_scrive_davvero(tmp_path):
    op = _operazioni(False)
    sorgente = tmp_path / 'a.txt'
    sorgente.write_text('contenuto', encoding='utf-8')
    cartella = tmp_path / 'sotto'

    assert op.crea_cartella(cartella) is True
    assert op.copia(sorgente, cartella / 'a.txt') is True

    assert (cartella / 'a.txt').read_text(encoding='utf-8') == 'contenuto'


def test_prova_a_vuoto_non_tocca_il_filesystem(tmp_path):
    op = _operazioni(True)
    sorgente = tmp_path / 'a.txt'
    sorgente.write_text('contenuto', encoding='utf-8')
    prima = sorted(p.name for p in tmp_path.iterdir())

    assert op.crea_cartella(tmp_path / 'sotto') is False
    assert op.copia(sorgente, tmp_path / 'sotto' / 'a.txt') is False
    assert op.rimuovi_file(sorgente) is False
    assert op.rinomina(sorgente, tmp_path / 'b.txt') is False

    assert sorted(p.name for p in tmp_path.iterdir()) == prima
    assert sorgente.read_text(encoding='utf-8') == 'contenuto'


def test_prova_a_vuoto_non_rimuove_un_albero(tmp_path):
    op = _operazioni(True)
    albero = tmp_path / 'albero'
    (albero / 'dentro').mkdir(parents=True)
    (albero / 'dentro' / 'x.txt').write_text('x', encoding='utf-8')

    assert op.rimuovi_albero(albero) is False

    assert (albero / 'dentro' / 'x.txt').exists()


def test_conteggi_crescono_in_entrambe_le_modalita(tmp_path):
    for prova_a_vuoto in (False, True):
        op = _operazioni(prova_a_vuoto)
        sorgente = tmp_path / f'src-{prova_a_vuoto}.txt'
        sorgente.write_text('x', encoding='utf-8')
        op.crea_cartella(tmp_path / f'dir-{prova_a_vuoto}')
        op.copia(sorgente, tmp_path / f'dir-{prova_a_vuoto}' / 'x.txt')

        assert op.conteggi['cartelle'] == 1
        assert op.conteggi['copie'] == 1


def test_riepilogo_dichiara_la_modalita():
    assert 'Prova a vuoto' in _operazioni(True).riepilogo()
    assert 'Operazioni eseguite' in _operazioni(False).riepilogo()


def test_rimozione_reale_elimina(tmp_path):
    op = _operazioni(False)
    bersaglio = tmp_path / 'togliere.txt'
    bersaglio.write_text('x', encoding='utf-8')

    assert op.rimuovi_file(bersaglio) is True
    assert not bersaglio.exists()


def test_copia_sovrascrive_una_destinazione_read_only(tmp_path):
    """Regressione: un file di destinazione read-only fa fallire copy2 con PermissionError
    prima ancora che possa riallineare i permessi (verificato il 2026-09-14 su un file reale
    lato OneDrive, indipendente dall'anonimizzazione)."""
    op = _operazioni(False)
    sorgente = tmp_path / 'nuovo.txt'
    sorgente.write_text('versione nuova', encoding='utf-8')
    destinazione = tmp_path / 'vecchio.txt'
    destinazione.write_text('versione vecchia', encoding='utf-8')
    destinazione.chmod(stat.S_IREAD)

    assert op.copia(sorgente, destinazione) is True

    assert destinazione.read_text(encoding='utf-8') == 'versione nuova'


def test_rimozione_reale_elimina_un_file_read_only(tmp_path):
    op = _operazioni(False)
    bersaglio = tmp_path / 'togliere.txt'
    bersaglio.write_text('x', encoding='utf-8')
    bersaglio.chmod(stat.S_IREAD)

    assert op.rimuovi_file(bersaglio) is True
    assert not bersaglio.exists()
