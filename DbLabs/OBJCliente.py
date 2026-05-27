import os

naturezas = ["Simples Nacional",
             "Lucro Real",
             "lucro Presumido"]

pastas = {}


if os.name == "nt":
    host = r"\\servidor\Ethos"
else:
    host = r"/mnt/win"


def getCaminho(caminho):

    if os.name == "nt":
        caminho = caminho.replace("/", "\\")
        return fr"\\servidor\Ethos\{caminho}"

    else:
        caminho = caminho.replace("\\","/")
        return rf"/mnt/win/{caminho}"




try:
    for natureza in naturezas:
        for pasta in os.listdir(getCaminho(fr"SERVIDOR/{natureza}/Clientes ativos")):

            codPasta = pasta.split(" - ")[-1]
            pastas[codPasta] = getCaminho(fr"SERVIDOR/{natureza}/Clientes ativos/{pasta}")

    del codPasta,pasta, naturezas, natureza
except FileNotFoundError as e:

    print(e)
except Exception as e:
    print(e)


class Cliente:
    def __init__(self, razao, cod, nomeFatasia, cnpj, ramo, dataInicio, situacao,regime, enderecoEmp, responsavelEmp):
        self.razao = razao
        self.cod = int(cod)
        self.nomeFantasia = nomeFatasia
        self.cnpj = cnpj
        self.regime = regime
        self.ramo = ramo
        self.dataEntrada = dataInicio
        self.ativa = situacao != "I"
        self.enderecoEmp = enderecoEmp
        self.responsavel = responsavelEmp
        self.toList = [cod, razao, cnpj, nomeFatasia, situacao, enderecoEmp, responsavelEmp]
        self.situacao = situacao

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

