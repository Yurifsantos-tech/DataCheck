"""Teste de Aula 49: usa banco SQLite temporario e NAO o banco real."""
import tempfile
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
# Requer banco.py/cadastro_db.py/recebimento_db.py na mesma pasta no Mac.
from unittest.mock import patch
import banco
from cadastro_db import preparar_cadastros
from recebimento_db import preparar_recebimentos, cadastrar_nota, adicionar_item, receber_nota
from operacoes_visual import cadastrar_fornecedor, registrar_venda

class TesteAula49(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patch = patch.object(banco,'CAMINHO_BANCO',Path(self.tmp.name)/'teste.db')
        self.patch.start()
        banco.criar_banco(); banco.cadastrar_produtos(); preparar_recebimentos()
    def tearDown(self):
        self.patch.stop(); self.tmp.cleanup()
    def test_fornecedor_e_nota(self):
        cadastrar_fornecedor('101','Distribuidora Teste','Recife','PE','50000-000','81999999999','Rua Teste 1')
        nid=cadastrar_nota('2001','1','29/10/2026','101')
        adicionar_item(nid,1,20,'14,00');adicionar_item(nid,2,15,'10,00')
        self.assertEqual(receber_nota(nid),43000)
        self.assertEqual(banco.consultar_produtos()[0][3],120)
        self.assertEqual(banco.consultar_produtos()[1][3],215)
        with self.assertRaises(ValueError): receber_nota(nid)
    def test_venda_rollback(self):
        with self.assertRaises(ValueError): registrar_venda([(1,999,'0')])
        self.assertEqual(banco.consultar_produtos()[0][3],100)
        vid,total=registrar_venda([(1,10,'1'),(2,5,'3')])
        self.assertEqual(total,27075)
        self.assertEqual(banco.consultar_produtos()[0][3],90)
        self.assertEqual(banco.consultar_produtos()[1][3],195)
        with banco.conectar() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM itens_venda WHERE venda_id=?',(vid,)).fetchone()[0],2)

if __name__=='__main__': unittest.main(verbosity=2)
