""" lista todos os certificados com o formato certo na pasta do servidor """

import os
import time
from datetime import datetime
from Ferramentas.printTool import colorizar
from Objetos.infoCert import certificadoLD
import DbLabs
from Objetos.CertificadoPJ import Certificado



bd = DbLabs.buscaDominio()


def formataData(data: datetime):
    dia = data.day
    mes = data.month
    if dia < 10: dia = f'0{data.day}'
    if mes < 10: mes = f'0{data.month}'

    return f'{dia}.{mes}.{data.year}'


def descarta(RAIZ, arquivo):
    try:
        os.rename(fr"{RAIZ}\{arquivo}",
                  fr"{RAIZ}\Inválidos\Validade expirada\{arquivo}")
        print(colorizar(f"\"{arquivo}\" Descartado", "vermelho"))


    except FileExistsError:

        i = 1

        while f"({i}) {arquivo}" in os.listdir(fr"{RAIZ}\Inválidos\Validade expirada"):
            i = i + 1

        os.rename(fr"{RAIZ}\{arquivo}",
                  fr"{RAIZ}\Inválidos\Validade expirada\({i}) {arquivo}")


def isCertificado(arquivo):
    if "pfx" in arquivo or "p12" in arquivo:
        return True
    else:
        return False


def descartaNaoCliente(RAIZ, arquivo):
    try:
        os.rename(fr"{RAIZ}\{arquivo}",
                  fr"{RAIZ}\Inválidos\Não clientes\{arquivo}")
        print(colorizar(f"\"{arquivo}\" Descartado como não cliente", "vermelho"))

    except FileExistsError:
        if arquivo in os.listdir(RAIZ):
            time.sleep(1)
            os.rename(fr"{RAIZ}\{arquivo}",
                      fr"{RAIZ}\Inválidos\{arquivo}")
        else:
            print(f"Problemas ao descartar {arquivo}\n")


def isFormatadoPJ(RAIZ, arquivo):
    splitNome = arquivo.split(' - ')

    cod = None
    novoArquivo = ""

    if len(splitNome) == 4:

        if splitNome[1].startswith(' '):
            print(f"Senha com espaço duplicada em {arquivo}")


    if len(splitNome) in [2, 3]:
        infos = certificadoLD(arquivo, RAIZ)

        cliente = bd.buscaCNPJ(infos.PF_PJ)
        if cliente is not None:
            cod = cliente.cod
        else:
            cod = "00"

        novoArquivo = fr"{infos.razao} - {splitNome[1].replace(".pfx", "")} - {formataData(infos.validade)} - {cod}.pfx"

        os.rename(fr"{RAIZ}\{arquivo}",
                  fr"{RAIZ}\{novoArquivo}")
        print(colorizar(f"{infos.razao} reformatado com codigo {cod}", "verde"))

    if cod != "00":
        return True

    else:
        descartaNaoCliente(RAIZ, novoArquivo)

    return False





class listaCert:


    def __init__(self):
        self.listaCertificadosPJ = []
        self.listaCertificadosPF = []
        self.naoCertificados = []
        self.socios = bd.querryToDF(

            r"""select distinct rleg_emp as responsavel,cpf_leg_emp as cpf, codi_emp, razao_emp as razao
                from bethadba.geempre
                where stat_emp != 'I' and
                      rleg_emp is not null
                                                                  """)




        self.listarCertificadosPJ()
        self.listarCertificadosPF()


    def isDuplicado(self, RAIZ, certAtual):

        for outroCert in self.listaCertificadosPJ:

            if outroCert.cod == certAtual.cod:
                print(colorizar(f"{certAtual.arquivo} Duplicado em {outroCert.arquivo}:\n", "amarelo"))

                if outroCert.validade >= certAtual.validade:

                    os.rename(fr"{RAIZ}\{certAtual.arquivo}",
                              fr"{RAIZ}\Inválidos\Duplicados\{certAtual.arquivo}")
                    print("\t" + colorizar(f"{certAtual.arquivo} Descartado como duplicado", "vermelho") + "\n" * 2)

                else:
                    try:
                        os.rename(fr"{RAIZ}\{outroCert.arquivo}",
                                  fr"{RAIZ}\Inválidos\Duplicados\{outroCert.arquivo}")
                        print("\t" + colorizar(f"{outroCert.arquivo} Descartado como duplicado", "vermelho") + "\n" * 2)

                    except FileExistsError:
                        print(fr" {outroCert.arquivo} Substituindo arquivo duplicado em inválidos\duplicados")
                        os.replace(fr"{RAIZ}\{outroCert.arquivo}",
                                   fr"self{RAIZ}\Inválidos\Duplicados\{outroCert.arquivo}", )

    def isFormatadoPF(self, RAIZ, arquivo):
        splitNome = arquivo.split(' - ')

        if len(splitNome) == 4:

            if splitNome[1].startswith(' '):
                print(f"Senha com espaço duplicada em {arquivo}")

            return True

        if len(splitNome) in [2, 3]:
            infos = certificadoLD(arquivo, RAIZ)

            if infos.PF_PJ is None:
                return False

            empresas = self.socios[self.socios['cpf'] == infos.PF_PJ]['razao'].tolist()

            if not empresas:
                empresas.append("Não cliente")

            novoArquivo = fr"{infos.razao} - {splitNome[1].replace(".pfx", "")} - {formataData(infos.validade)} - {empresas[0]}.pfx"


            os.rename(fr"{RAIZ}\{arquivo}",
                      fr"{RAIZ}\{novoArquivo}")

            print(colorizar(f"{infos.razao} anotação atualizada {empresas[0]}", "verde"))

            return True

        return False

    def listarCertificadosPJ(self):

        RAIZ = fr"\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CNPJ"

        arquivos = os.listdir(RAIZ)
        for arquivo in arquivos:

            if isFormatadoPJ(RAIZ, arquivo) and isCertificado(arquivo):
                try:
                    cert = Certificado(arquivo, RAIZ)

                    if cert.valido and cert.isCliente:


                        self.isDuplicado(RAIZ, cert)
                        self.listaCertificadosPJ.append(cert)

                    elif not cert.isCliente:
                        descartaNaoCliente(RAIZ, cert.arquivo)

                    else:
                        descarta(RAIZ, cert.arquivo)

                except IndexError as e:


                    print(arquivo, "Formatado incorretamente", "\n")

                except AttributeError as e:
                    print(arquivo, e, "\n")

                self.naoCertificados.append(arquivo)

    def listarCertificadosPF(self):

        RAIZ = fr"\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CPF"

        arquivos = os.listdir(RAIZ)
        for arquivo in arquivos:

            if self.isFormatadoPF(RAIZ, arquivo) and isCertificado(arquivo):
                try:
                    cert = Certificado(arquivo, RAIZ)

                    nota = arquivo.split(' - ')[3]

                    if nota == "Não cliente.pfx":
                        os.rename(fr"{RAIZ}\{arquivo}",
                                  fr"{RAIZ}\Não Cliente\{arquivo}")



                    if cert.valido:

                        self.isDuplicado(RAIZ, cert)
                        self.listaCertificadosPF.append(cert)

                    else:
                        descarta(RAIZ, cert.arquivo)

                except IndexError as e:
                    print(arquivo, e, "\n")

                except AttributeError as e:
                    print(arquivo, e, "\n")

                self.naoCertificados.append(arquivo)