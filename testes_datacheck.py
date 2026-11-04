"""Testes sem alterar o banco real do usuario. Execute: python3 -m unittest -v testes_datacheck.py"""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import banco
import seguranca_admin
from backup_sqlite import realizar_backup


class TestesDataCheck(unittest.TestCase):
    def test_backup_copia_dados_e_integridade(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            origem = pasta / 'origem.db'
            with sqlite3.connect(origem) as db:
                db.execute('CREATE TABLE teste (valor INTEGER NOT NULL)')
                db.execute('INSERT INTO teste VALUES (43)')
            copia = realizar_backup(origem, pasta / 'copias')
            with sqlite3.connect(copia) as db:
                self.assertEqual(db.execute('SELECT valor FROM teste').fetchone()[0], 43)
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')

    def test_senha_correta_e_incorreta(self):
        with tempfile.TemporaryDirectory() as pasta:
            config = Path(pasta) / 'admin_config.json'
            with patch.object(seguranca_admin, 'ARQUIVO', config):
                with patch('getpass.getpass', side_effect=['Teste2026', 'Teste2026']):
                    seguranca_admin.cadastrar_admin()
                self.assertTrue(seguranca_admin.autenticar('Teste2026'))
                self.assertFalse(seguranca_admin.autenticar('senha-incorreta'))

    def test_rejeita_senha_curta(self):
        with tempfile.TemporaryDirectory() as pasta:
            config = Path(pasta) / 'admin_config.json'
            with patch.object(seguranca_admin, 'ARQUIVO', config):
                with patch('getpass.getpass', side_effect=['curta', 'curta']):
                    seguranca_admin.cadastrar_admin()
                self.assertFalse(config.exists())

    def test_banco_tem_esquema_basico_em_arquivo_temporario(self):
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / 'teste.db'
            def conectar_teste():
                db = sqlite3.connect(destino)
                db.execute('PRAGMA foreign_keys = ON')
                return db
            with patch.object(banco, 'conectar', conectar_teste):
                banco.criar_banco()
            with sqlite3.connect(destino) as db:
                nomes = {x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertTrue({'produtos', 'vendas', 'itens_venda'}.issubset(nomes))


if __name__ == '__main__':
    unittest.main(verbosity=2)
