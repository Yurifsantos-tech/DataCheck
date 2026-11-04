"""Aula 47: backup consistente do banco SQLite com API de backup nativa."""
import sqlite3
from datetime import datetime
from pathlib import Path
from banco import CAMINHO_BANCO

DESTINO = Path(__file__).resolve().parent / 'backups'


def realizar_backup(origem=CAMINHO_BANCO, destino_pasta=DESTINO):
    origem = Path(origem)
    if not origem.is_file():
        raise FileNotFoundError(f'Banco nao encontrado: {origem}')
    destino_pasta = Path(destino_pasta)
    destino_pasta.mkdir(parents=True, exist_ok=True)
    nome = f"datacheck_{datetime.now():%Y%m%d_%H%M%S_%f}.db"
    destino = destino_pasta / nome
    try:
        with sqlite3.connect(f'file:{origem.resolve()}?mode=ro', uri=True) as fonte:
            with sqlite3.connect(destino) as copia:
                fonte.backup(copia)
                resultado = copia.execute('PRAGMA integrity_check').fetchone()[0]
                if resultado != 'ok':
                    raise RuntimeError(f'Falha na integridade da copia: {resultado}')
    except Exception:
        destino.unlink(missing_ok=True)
        raise
    return destino


if __name__ == '__main__':
    try:
        print('Backup criado e verificado:', realizar_backup())
    except Exception as erro:
        print('Backup nao realizado:', erro)
        raise SystemExit(1)
