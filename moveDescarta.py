from PrintTool import printTool
import os
import secrets

vermelho = printTool.configColorizar('vermelho', autoPrint=True).colorizar
verde = printTool.configColorizar('verde', autoPrint=True).colorizar
amarelo = printTool.configColorizar('amarelo', autoPrint=True).colorizar
roxo = printTool.configColorizar('rosa', autoPrint=False).colorizar

def renomeia(linha,p):

    if p == 'PF':
        raiz = fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CPF'

        info = {
            'nome': linha['nome'],
            'senha': linha['senha'],
            'validade': linha['validade'].strftime("%d.%m.%Y"),
            'razao': linha['razao'],
            'tipo': linha['original'][-4:]}

        original = linha['original']
        novo = f"{info['nome']} - {info['senha']} - {info['validade']} - {info['razao']}{info['tipo']}"

    else:
        raiz = fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CNPJ'

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
        os.rename(
            fr"{raiz}\{original}",
            fr"{raiz}\{novo}"
        )

    except FileExistsError:
        try:
            os.rename(
                f"{raiz}/{original}",
                f"{raiz}/Inválidos/Duplicados/{novo}"
            )
        except FileExistsError:

            os.rename(
                f"{raiz}/{original}",
                f"{raiz}/Inválidos/Duplicados/{novo}{secrets.randbits(15)}"
            )

    verde(f'\n{original}:\n'
          f'{novo}\n')


def descartaValidade(linha,p,subpasta=''):
    if p == 'PF':
        raiz = fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CPF'

        info = {
            'nome': linha['nome'],
            'senha': linha['senha'],
            'validade': linha['validade'].strftime("%d.%m.%Y"),
            'razao': linha['razao'],
            'tipo': linha['original'][-4:]}

        original = linha['original']
        novo = f"{info['nome']} - {info['senha']} - {info['validade']} - {info['razao']}{info['tipo']}"

    else:
        raiz = fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CNPJ'

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
        os.rename(
            fr"{raiz}\{subpasta}{original}",
            fr"{raiz}\Inválidos\Validade expirada\{novo}"
        )
        amarelo(f'Vencido: {novo}')

    except FileExistsError:

        os.remove(fr'{raiz}\{subpasta}{original}')
        amarelo(f'Vencido e duplicado: {original} deletado')


def descartaNaoCliente(linha, p):

    if p == 'PF':
        raiz = fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CPF'

        info = {
            'nome': linha['nome'],
            'senha': linha['senha'],
            'validade': linha['validade'].strftime("%d.%m.%Y"),
            'razao': 'Não Cliente',
            'tipo': linha['original'][-4:]}

        original = linha['original']
        novo = fr"{info['nome']} - {info['senha']} - {info['validade']} - {info['razao']}{info['tipo']}"
        pasta = f"\\Não Cliente\\"

    else:
        raiz = fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CNPJ'

        infos = {
            'razao': linha['razao'],
            'senha': linha['senha'],
            'validade': linha['validade'].strftime("%d.%m.%Y"),
            'cod': int(linha['cod']),
            'tipo': linha['original'][-4:],
        }

        original = linha['original']
        novo = fr"{infos['razao']} - {infos['senha']} - {infos['validade']} - {infos['cod']}{infos['tipo']}"
        pasta = f"\\Inválidos\\Não clientes\\"
    try:
        os.rename(
            fr"{raiz}\{original}",
            fr"{raiz}{pasta}{novo}"
        )

    except FileExistsError:

        os.rename(
            fr"{raiz}\{original}",
            fr"{raiz}\Inválidos\Duplicados\{original}{secrets.randbits(15)}")

    vermelho(fr'Não cliente {novo}')
