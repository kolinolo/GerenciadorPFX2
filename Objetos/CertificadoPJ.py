import os
from datetime import date

from Objetos.infoCert import certificadoLD
from DbLabs import buscaDominio
bd = buscaDominio()


def formataData(data):
    dia = data.day
    mes = data.month
    if dia < 10: dia = f'0{data.day}'
    if mes < 10: mes = f'0{data.month}'

    return f'{dia}.{mes}.{data.year}'


class Certificado:
    def __init__(self, arquivo, RAIZ):
        infos = arquivo.split(' - ')
        self.razao = infos[0]
        self.senha = infos[1]
        self.cod = infos[3].split('.')[0]
        self.arquivo = arquivo
        self.valido = False
        self.isCliente = False
        self.RAIZ = RAIZ
        infoDoArquivo = certificadoLD(self.arquivo,self.RAIZ)

        dataAtual = date.today()

        validadeDoArquivo = infoDoArquivo.validade
        self.cnpj = infoDoArquivo.PF_PJ

        if bd.buscaCNPJ(self.cnpj) is None:

            self.isCliente = False

        else:
            self.isCliente = True

        validade = infos[2]
        validade = validade.split('.')
        self.validade = date(int(validade[2]), int(validade[1]), int(validade[0]))

        if self.validade != validadeDoArquivo:
            print(f"Validade diferente em {arquivo}")
            self.redatar(validadeDoArquivo)

        if self.validade >= dataAtual:
            self.valido = True

        else:
            self.valido = False

    def renomear(self, novoNome):

        nomeAntigo = self.razao
        arquivoAntigo = self.arquivo

        self.razao = novoNome

        self.arquivo = self.arquivo.replace(nomeAntigo, novoNome)
        os.rename(f"{self.RAIZ}\\{arquivoAntigo}",
                  f"{self.RAIZ}\\{self.arquivo}")

    def redatar(self, data):

        dataAntiga = formataData(self.validade)
        novaData = formataData(data)

        arquivoAntigo = self.arquivo
        self.arquivo = self.arquivo.replace(dataAntiga, novaData)
        self.validade = data

        try:
            os.rename(f"{self.RAIZ}\\{arquivoAntigo}",
                      f"{self.RAIZ}\\{self.arquivo}")
        except FileExistsError:

            i = 0
            while self.arquivo in os.listdir(fr"{self.RAIZ}\Inválidos\Duplicados"):

                i = i + 1


                os.rename(f"{self.RAIZ}\\{arquivoAntigo}",
                          f"{self.RAIZ}\\Inválidos\\Duplicados\\{self.arquivo}({i})")


