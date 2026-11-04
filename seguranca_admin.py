"""Aula 46: autenticacao local de administrador (nao integrada aos menus antigos)."""
import getpass
import hashlib
import hmac
import json
import os
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent / 'dados' / 'admin_config.json'
ITERACOES = 600_000


def senha_valida(senha):
    """Regra didatica local: 5 a 12 caracteres ASCII, letras e numeros presentes."""
    return (5 <= len(senha) <= 12
            and senha.isascii()
            and senha.isalnum()
            and any(c.isalpha() for c in senha)
            and any(c.isdigit() for c in senha))


def derivar(senha, sal):
    return hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), sal, ITERACOES).hex()


def cadastrar_admin():
    if ARQUIVO.exists():
        print('Administrador ja configurado. Nada foi alterado.')
        return
    senha = getpass.getpass('Defina uma senha (5 a 12 caracteres, letras e numeros): ')
    confirmacao = getpass.getpass('Confirme a senha: ')
    if not senha_valida(senha):
        print('Senha invalida: use de 5 a 12 caracteres, com letras e numeros, sem espacos ou simbolos.')
        return
    if senha != confirmacao:
        print('As senhas digitadas sao diferentes. Nenhum cadastro criado.')
        return
    sal = os.urandom(16)
    ARQUIVO.parent.mkdir(exist_ok=True)
    config = {'versao': 1, 'sal': sal.hex(), 'hash': derivar(senha, sal)}
    try:
        with ARQUIVO.open('x', encoding='utf-8') as f:
            json.dump(config, f)
        os.chmod(ARQUIVO, 0o600)
    except FileExistsError:
        print('Administrador ja configurado.')
        return
    print('Senha administrativa configurada.')


def autenticar(senha):
    if not ARQUIVO.exists():
        return False
    try:
        config = json.loads(ARQUIVO.read_text(encoding='utf-8'))
        calculado = derivar(senha, bytes.fromhex(config['sal']))
        return hmac.compare_digest(calculado, config['hash'])
    except (ValueError, KeyError, OSError, TypeError):
        return False


def main():
    if not ARQUIVO.exists():
        cadastrar_admin()
    else:
        senha = getpass.getpass('Senha administrativa para verificar: ')
        print('Autenticacao aprovada.' if autenticar(senha) else 'Autenticacao negada.')


if __name__ == '__main__':
    main()
