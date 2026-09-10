"""Test dell'ancoraggio in locale.

Su un albero normale, cioe' non gestito da un client cloud, gli attributi `PINNED` e `UNPINNED`
si possono comunque impostare e rileggere: e' quello che questi test verificano. Cio' che non
si puo' verificare qui e' che un client cloud reale li rispetti, che dipende da lui e non da
questo codice, e va provato sul campo prima di puntare il watcher a una cartella cloud vera.
"""

import logging

import pytest

from folder_sync_watcher import pin
from folder_sync_watcher.operazioni import OperazioniFile

pytestmark = pytest.mark.skipif(pin._kernel32 is None, reason="API di Windows non disponibili")


def _logger():
    lg = logging.getLogger('test_pin')
    lg.addHandler(logging.NullHandler())
    return lg


def _albero(tmp_path):
    (tmp_path / 'a' / 'b').mkdir(parents=True)
    (tmp_path / 'a' / 'uno.txt').write_text('1', encoding='utf-8')
    (tmp_path / 'a' / 'b' / 'due.txt').write_text('2', encoding='utf-8')
    return tmp_path


def test_ancora_un_singolo_file(tmp_path):
    f = tmp_path / 'x.txt'
    f.write_text('x', encoding='utf-8')

    assert pin.ancora(f) is True
    assert pin.e_ancorato(f) is True


def test_ancora_albero_copre_tutto(tmp_path):
    radice = _albero(tmp_path)

    esito = pin.ancora_albero(radice, _logger())

    assert esito['esaminati'] == 5  # la radice, le cartelle a e a/b, e i due file
    assert esito['non_ancorati'] == 0
    assert esito['ancorati'] == esito['esaminati']


def test_ancora_albero_supera_il_limite_dei_260_caratteri(tmp_path):
    """Regressione: attrib.exe salta in silenzio i percorsi lunghi, questo codice no."""
    profondo = tmp_path
    for _ in range(12):
        profondo = profondo / ('segmento_lungo_' + 'x' * 20)
    profondo.mkdir(parents=True)
    bersaglio = profondo / 'in-fondo.txt'
    bersaglio.write_text('y', encoding='utf-8')
    assert len(str(bersaglio)) > 260

    esito = pin.ancora_albero(tmp_path, _logger())

    assert esito['non_ancorati'] == 0
    assert pin.e_ancorato(bersaglio) is True


def test_prova_a_vuoto_non_ancora_nulla(tmp_path):
    radice = _albero(tmp_path)
    op = OperazioniFile(_logger(), prova_a_vuoto=True)

    esito = pin.ancora_albero(radice, _logger(), op)

    assert esito['simulati'] == esito['esaminati']
    assert esito['ancorati'] == 0
    assert pin.e_ancorato(radice / 'a' / 'uno.txt') is False


def test_radice_inesistente_non_solleva(tmp_path):
    esito = pin.ancora_albero(tmp_path / 'non-esiste', _logger())

    assert esito['esaminati'] == 0
