import datetime
import os



from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import pkcs12



class certificadoLD:
    def __init__(self, arquivo, RAIZ):
        self.razao: str = None
        self.arquivo: str = arquivo
        self.criacao: datetime.date = None
        self.validade: datetime.date = None
        self.PF_PJ: str = None
        self.RAIZ = RAIZ
        self.senha = self.arquivo.split(" - ")[1].replace(".pfx", "")



        self.getInfo()

        if "E-CNPJ" in RAIZ: tamanho = 14
        else: tamanho = 11



    def getInfo(self):
        # Caminho do arquivo e senha

        pfx_password = self.arquivo.split(" - ")[1].replace(".pfx", "")  # A senha precisa ser em bytes

        if '[asterisco]' in pfx_password:
            pfx_password = pfx_password.replace('[asterisco]', '*')

        pfx_password = pfx_password.encode()

        try:
            # Ler o arquivo
            with open(rf'{self.RAIZ}\{self.arquivo}', "rb") as f:
                criptografado = f.read()
                infos = pkcs12.load_key_and_certificates(criptografado, pfx_password, backend=default_backend())[1]
                self.criacao = infos.not_valid_before_utc.date()
                self.validade = infos.not_valid_after_utc.date()
                self.PF_PJ = infos.subject.rdns[-1].rfc4514_string().split(":")[1]
                self.razao = infos.subject.rdns[-1].rfc4514_string().split(":")[0].replace("CN=", "")

        except:

            print(self.arquivo, "Senha Invalida")

