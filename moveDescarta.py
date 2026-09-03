from pathlib import Path

from PrintTool import printTool
import os
import secrets

vermelho = printTool.configColorizar('vermelho', autoPrint=True).colorizar
verde = printTool.configColorizar('verde', autoPrint=True).colorizar
amarelo = printTool.configColorizar('amarelo', autoPrint=True).colorizar
roxo = printTool.configColorizar('rosa', autoPrint=False).colorizar

def renomeia(linha,p):

    if p == 'PF':
        raiz = Path(fr"{os.getenv('RAIZ')}/Certificados digitais/E-CPF")

        info = {
            'nome': linha['nome'],
            'senha': linha['senha'],
            'validade': linha['validade'].strftime("%d.%m.%Y"),
            'razao': linha['razao'],
            'tipo': linha['original'][-4:]}

        original = linha['original']
        novo = f"{info['nome']} - {info['senha']} - {info['validade']} - {info['razao']}{info['tipo']}"

    else:
        raiz = Path(fr'{os.getenv('RAIZ')}/Certificados digitais/E-CNPJ')

        infos = {
            'razao': linha['razao'],
            'senha': linha['senha'],
            'validade': linha['validade'].strftime("%d.%m.%Y"),
            'cod':int(linha['cod']),
            'tipo': linha['original'][-4:],
        }

        original = linha['original']
        novo = f"{infos['razao']} - {infos['senha']} - {infos['validade']} - {infos['cod']}{infos['tipo']}"


    try:
        Path(f"{raiz}/{original}").rename(fr"{raiz}/{novo}")

    except FileExistsError:
        try:

            Path(f"{raiz}/{original}").rename(f"{raiz}/Inválidos/Duplicados/{novo}")

        except FileExistsError:

            Path(f"{raiz}/{original}").rename(f"{raiz}/Inválidos/Duplicados/{secrets.randbits(15)}-{novo}")


    verde(f'\n{original}:\n'
          f'{novo}\n')


def descartaValidade(linha,p,subpasta=''):
    if p == 'PF':
        raiz = Path(fr'{os.getenv('RAIZ')}/Certificados digitais/E-CPF')

        info = {
            'nome': linha['nome'],
            'senha': linha['senha'],
            'validade': linha['validade'].strftime("%d.%m.%Y"),
            'razao': linha['razao'],
            'tipo': linha['original'][-4:]}

        original = linha['original']
        novo = f"{info['nome']} - {info['senha']} - {info['validade']} - {info['razao']}{info['tipo']}"

    else:
        raiz = Path(fr'{os.getenv('RAIZ')}/Certificados digitais/E-CNPJ')

        infos = {
            'razao': linha['razao'],
            'senha': linha['senha'],
            'validade': linha['validade'].strftime("%d.%m.%Y"),
            'cod': int(linha['cod']),
            'tipo': linha['original'][-4:],
        }

        original = linha['original']
        novo = f"{infos['razao']} - {infos['senha']} - {infos['validade']} - {infos['cod']}{infos['tipo']}"

    try:
        Path(
            fr"{raiz}/{subpasta}{original}").rename(fr"{raiz}/Inválidos/Validade expirada/{novo}")

        amarelo(f'Vencido: {novo}')

    except FileExistsError:

        Path(fr'{raiz}/{subpasta}{original}').unlink()
        amarelo(f'Vencido e duplicado: {original} deletado')


def descartaNaoCliente(linha, p):

    if p == 'PF':
        raiz = Path(fr'{os.getenv('RAIZ')}/Certificados digitais/E-CPF')

        info = {
            'nome': linha['nome'],
            'senha': linha['senha'],
            'validade': linha['validade'].strftime("%d.%m.%Y"),
            'razao': 'Não Cliente',
            'tipo': linha['original'][-4:]}

        original = linha['original']
        novo = fr"{info['nome']} - {info['senha']} - {info['validade']} - {info['razao']}{info['tipo']}"
        pasta = f"/Não Cliente/"

    else:
        raiz = fr'{os.getenv('RAIZ')}/Certificados digitais/E-CNPJ'

        infos = {
            'razao': linha['razao'],
            'senha': linha['senha'],
            'validade': linha['validade'].strftime("%d.%m.%Y"),
            'cod': int(linha['cod']),
            'tipo': linha['original'][-4:],
        }

        original = linha['original']
        novo = fr"{infos['razao']} - {infos['senha']} - {infos['validade']} - {infos['cod']}{infos['tipo']}"
        pasta = f"/Inválidos/Não clientes/"
    try:
        Path(fr"{raiz}/{original}").rename(fr"{raiz}{pasta}{novo}")



    except FileExistsError:

        Path(fr"{raiz}/{original}").rename(fr"{raiz}/Inválidos/Duplicados/{secrets.randbits(15)}-{original}")

    vermelho(fr'Não cliente {novo}')
