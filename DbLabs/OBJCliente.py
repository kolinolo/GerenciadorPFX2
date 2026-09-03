import os
from pathlib import Path

naturezas = ["Simples Nacional",
             "Lucro Real",
             "Lucro Presumido"]

pastas = {}



raiz = Path(os.getenv('RAIZ'))



try:
    for natureza in naturezas:
        for pasta in  [p.name for p in  Path(fr"{raiz}/{natureza}/Clientes ativos").iterdir()]:

            codPasta = pasta.split(" - ")[-1]
            pastas[codPasta] = Path(fr"{raiz}/{natureza}/Clientes ativos/{pasta}")

    del codPasta,pasta, naturezas, natureza
except FileNotFoundError as e:

    print(e)
except Exception as e:
    print(e)


class Cliente:
    def __init__(self, razao, cod, nomeFatasia, cnpj, ramo, dataInicio,dataInativada, situacao,regime, enderecoEmp, responsavelEmp,cnae,i_estadual,  socios = list):
        self.razao = razao
        self.cod = int(cod)
        self.nomeFantasia = nomeFatasia
        self.cnpj = cnpj
        self.regime = regime
        self.ramo = ramo
        self.dataEntrada = dataInicio
        self.dataInativada = dataInativada
        self.ativa = situacao != "I"
        self.enderecoEmp = enderecoEmp
        self.responsavel = responsavelEmp
        self.toList = [cod, razao, cnpj, nomeFatasia, situacao, enderecoEmp, responsavelEmp]
        self.situacao = situacao
        self.cnae = cnae
        self.socios = socios
        self.i_estadual = i_estadual


    def __str__(self):
        return f"{self.razao} - {self.cod}"

    def __repr__(self):
        return self.__str__()

    def filial(self):
        if self.cnpj is None: return False
        return "0001" not in self.cnpj

    def getPasta(self):

        return pastas[str(self.cod)]



class responsavel:

    def __init__(self, nome, cpf, enderecoResp):
        self.nome = nome
        self.cpf = cpf
        self.endereco = enderecoResp

    def __str__(self):
        return f"{self.nome}"

    def __repr__(self):
        return self.__str__()

class endereco:

    def __init__(self, cep, bairro, logradouro, numero, estado, municipio):
        self.cep = cep
        self.endereco = endereco
        self.bairro = bairro
        self.logradouro = logradouro
        self.numero = numero
        self.estado = estado
        self.municipio = municipio

        self.usual = f"{logradouro}, {numero}, {municipio}"

    def __str__(self):
        return self.usual

    def __repr__(self):
        return self.__str__()

