from .OBJCliente import endereco, Cliente, responsavel
import pandas as pd
import sqlanydb
import warnings
import os

from .consultaPostgress import getClientesBase, querryToDFPG, executaComando, appendDF
from .exceptions import CNPJInvalido


from dotenv import load_dotenv

load_dotenv(r".env")

warnings.simplefilter(action='ignore', category=UserWarning)
print("DBLabs iniciado no AutoBalanco")

QUERYBASE = """
            WITH municipios as (SELECT codigo_municipio as cod_mun, nome_municipio as municipio FROM bethadba.gemunicipio) 


            SELECT codi_emp      as cod, 
                   razao_emp     as razao, 
                   cgce_emp      as CNPJ, 
                   fantasia_emp  as nomeFantasia, 
                   ramo_emp      as Ramo,
                   mun.municipio as municipio, 
                   cepe_emp      as cepe, 
                   bair_emp      as bairro, 
                   ende_emp      as logradouro, 
                   nume_emp      as numero,
                   esta_emp      as estado, 
                   cep_leg_emp   as cepeResp, 
                   stat_emp      as situacao, 
                   bair_leg_emp     bairro_resp,
                   end_leg_emp   as logradouro_resp, 
                   nume_leg_emp  as numero_resp, 
                   mun_leg_emp   as municipio_resp, 
                   rleg_emp      as nome_resp,
                   cpf_leg_emp   as cpf_resp, 
                   dcad_emp  as dataInicio, 
                   dina_emp  as dataInativada, 
                   i_cnae20   as cnae,
                    iest_emp as i_estadual


            FROM bethadba.geempre emp 
                     join municipios mun ON emp.codigo_municipio = mun.cod_mun
            where cod < 900 

            """

QUERYSOCIOS = """select  s1.nome ,s1.inscricao as cpf,e.codi_emp as cod,
        e.razao_emp as razao, e.cpf_leg_emp
from bethadba.gequadrosocietario_socios s join bethadba.gesocios s1
    on s1.i_socio = s.i_socio

left join bethadba.geempre e on s.codi_emp = e.codi_emp
order by s1.nome"""


class buscaPostgres:
    getClientesBase = staticmethod(getClientesBase)
    querryToDFPG = staticmethod(querryToDFPG)
    executaComando = staticmethod(executaComando)
    appendDF = staticmethod(appendDF)


class buscaDominio:

    def __init__(self):

        self.pwd = os.getenv('PWDSQLANYWHERE')
        self.uid = os.getenv('USERSQLANYWHERE')
        self.host = f'{os.getenv('SERVIDOR')}:{os.getenv('PORTASQLANYWHERE')}'


        self.DFB = pd.merge(self.querryToDF(QUERYBASE), self.tabelaRegimes()[['cod','regime']], on='cod', how='left')
        self.DFB['regime'] = self.DFB['regime'].fillna('')
        self.DFB['cnae'] = self.DFB['cnae'].fillna('')
        self.DFB = self.DFB.sort_values(by=['cod'], ascending=True)


        self.dfSocios = self.querryToDF(QUERYSOCIOS)

        self.listaClientes = []
        self.ultimoCliente = 0
        self.listarClientes()

    def novaConexao(self):

        sucesso = False
        falhas = 0
        conexao = None

        while not sucesso:

            try:
                conexao = sqlanydb.connect(uid=self.uid,
                                           pwd=self.pwd,
                                           host=self.host,
                                           AutoStop="Yes",
                                           charset='latin1')
                sucesso = True

            except Exception as e:
                falhas = falhas + 1

                if falhas == 1:
                    print(e)
                print(f"Falha : {falhas} ")

        return conexao

    def listarClientes(self,orderByRazao=True):

        clientes = []

        for linha in range(len(self.DFB)):

            enderecoResp = endereco(self.DFB.at[linha, 'cepeResp'],
                                    self.DFB.at[linha, 'bairro_resp'],
                                    self.DFB.at[linha, 'logradouro_resp'],
                                    self.DFB.at[linha, 'numero_resp'],
                                    self.DFB.at[linha, 'estado'],
                                    self.DFB.at[linha, 'municipio_resp'])

            enderecoCliente = endereco(self.DFB.at[linha, 'cepe'],
                                       self.DFB.at[linha, 'bairro'],
                                       self.DFB.at[linha, 'logradouro'],
                                       self.DFB.at[linha, 'numero'],
                                       self.DFB.at[linha, 'estado'],
                                       self.DFB.at[linha, 'municipio'])

            responsavelLeg = responsavel(self.DFB.at[linha, 'nome_resp'],
                                         self.DFB.at[linha, 'cpf_resp'],
                                         enderecoResp)

            cliente = Cliente(self.DFB.at[linha, 'razao'],
                              self.DFB.at[linha, 'cod'],
                              self.DFB.at[linha, 'nomeFantasia'],
                              self.DFB.at[linha, 'CNPJ'],
                              self.DFB.at[linha, 'Ramo'],
                              self.DFB.at[linha, 'dataInicio'],
                              self.DFB.at[linha, 'dataInativada'],
                              self.DFB.at[linha, 'situacao'],
                              self.DFB.at[linha, 'regime'],
                              enderecoCliente, responsavelLeg,
                              self.DFB.at[linha, 'cnae'],
                              self.DFB.at[linha, 'i_estadual'],
                              socios = self.getSocios(self.DFB.at[linha, 'cod']))

            if self.ultimoCliente < cliente.cod:
                self.ultimoCliente = cliente.cod

            clientes.append(cliente)

        if orderByRazao:
            for ct in range(len(clientes)):  # Cliente atual

                for cc in range(ct, len(clientes)):  # Comparativo

                    if clientes[ct].razao > clientes[cc].razao:
                        tempCliente = clientes[ct]
                        clientes[ct] = clientes[cc]
                        clientes[cc] = tempCliente

        self.listaClientes = clientes
        return clientes

    def buscaRamoAproximado(self, stringDoRamo):
        clientesDoRamo = []

        for clienteAtual in self.listarClientes():
            ramo = str(clienteAtual.ramo)

            if str(stringDoRamo) in str(ramo) and not clienteAtual.filial() and clienteAtual.situacao == "A":
                clientesDoRamo.append(clienteAtual)

        for ca in range(len(clientesDoRamo)):
            for co in range(ca, len(clientesDoRamo)):

                if clientesDoRamo[ca].cod > clientesDoRamo[co].cod:
                    temp = clientesDoRamo[ca]
                    clientesDoRamo[ca] = clientesDoRamo[co]
                    clientesDoRamo[co] = temp

        for item in clientesDoRamo:
            print(f"{item.cod} - {item.razao} - {item.cnpj}")

        return clientesDoRamo

    def buscaCNPJ(self, CNPJ: str)-> Cliente|None:


        CNPJ = CNPJ.replace(".", "")
        CNPJ = CNPJ.replace("/", "")
        CNPJ = CNPJ.replace("-", "")
        CNPJ = CNPJ.replace(" ", "")


        if len(CNPJ) not in  (14, 12 , 8):
            raise CNPJInvalido(CNPJ)

        for temp in self.listaClientes:

            if temp.cnpj == CNPJ or temp.cnpj.startswith(CNPJ):
                return temp

        return None

    def buscaPorCod(self, cod):

        for temp in self.listaClientes:
            if str(temp.cod) == str(cod):
                return temp
        return None

    def buscaRazao(self, razao):

        for c in self.listaClientes:
            if c.razao == razao:
                return c

        return None

    def querryToDF(self, comando):

        conexao = self.novaConexao()
        cursor = conexao.cursor()
        cursor.execute(comando)
        dataFrame = pd.read_sql(comando, conexao)
        cursor.close()
        conexao.close()

        return dataFrame

    def querryToCSV(self, comando):

        return self.querryToDF(comando).to_csv()

    def listaAtivos(self):
        clientesAtivos = []
        for cliente in self.listaClientes:
            if cliente.ativa:
                clientesAtivos.append(cliente)

        return clientesAtivos

    def getFiliaisDF(self):

        q = """SELECT codi_emp  as cod, \
                      cgce_emp  as cnpj,
                      razao_emp as razao
               FROM bethadba.geempre \
               where cgce_emp not REGEXP '(.)*0001(.)*' and cod < 900"""

        df: pd.DataFrame = self.querryToDF(q).astype({'cod':str})
        return df

    def getMatrizDF(self):

        q = """SELECT codi_emp  as cod, \
                      cgce_emp  as cnpj,
                      razao_emp as razao
               FROM bethadba.geempre \
               where cgce_emp REGEXP '(.)*0001(.)*' and cod < 900"""

        df: pd.DataFrame = self.querryToDF(q).astype({'cod':str})

        return df

    def associaFiliais(self):
        matrizes = {}

        FL = self.getFiliaisDF()
        MT = self.getMatrizDF()

        for matriz in range(len(MT)):

            for filial in range(len(FL)):

                if FL['cnpj'].get(filial)[:7] == MT['cnpj'].get(matriz)[:7]:
                    if MT['cod'].get(matriz) not in matrizes.keys():
                        matrizes[MT['cod'].get(matriz)] = [FL['cod'].get(filial)]
                    else:
                        matrizes[MT['cod'].get(matriz)].append(FL['cod'].get(filial))
        return matrizes

    @staticmethod
    def organizaListaClientes(clientes, byCod=True):

        if byCod:

            for ct in range(len(clientes)):  # Cliente atual

                for cc in range(ct, len(clientes)):  # Comparativo

                    if clientes[ct].cod > clientes[cc].cod:
                        tempCliente = clientes[ct]
                        clientes[ct] = clientes[cc]
                        clientes[cc] = tempCliente

        else:
            for ct in range(len(clientes)):  # Cliente atual

                for cc in range(ct, len(clientes)):  # Comparativo

                    if clientes[ct].razao > clientes[cc].razao:
                        tempCliente = clientes[ct]
                        clientes[ct] = clientes[cc]
                        clientes[cc] = tempCliente

        return clientes

    def tabelaRegimes(self):

        sql = """

              SELECT geempre.razao_emp as razao,
                     geempre.codi_emp as cod,
                     geempre.stat_emp as stat,

                     EFPARAMETRO_VIGENCIA.RFED_PAR regime

              FROM bethadba.geempre,
                   bethadba.EFPARAMETRO_VIGENCIA

              WHERE EFPARAMETRO_VIGENCIA.VIGENCIA_PAR = (SELECT max(EFPARAMETRO_VIGENCIA.VIGENCIA_PAR)
                                                         FROM bethadba.EFPARAMETRO_VIGENCIA
                                                         WHERE geempre.codi_emp = EFPARAMETRO_VIGENCIA.CODI_EMP)
                AND geempre.codi_emp = EFPARAMETRO_VIGENCIA.CODI_EMP


              """

        df = self.querryToDF(sql).astype({'regime': str})

        df.loc[df['regime'] == '1', 'regime'] = 'Lucro Real'
        df.loc[df['regime'].isin(('2', '3', '4', '8', '9')), 'regime'] = 'Simples Nacional'
        df.loc[df['regime'] == '5', 'regime'] = 'Lucro Presumido'
        df.loc[df['regime'] == '6', 'regime'] = 'RET'

        return df

    def isSN(self,cods: tuple|list|str):

        df = self.tabelaRegimes().astype({'cod':str})
        df = df[df['regime'] == 'Simples Nacional']

        sn = df['cod'].tolist()


        if type(cods) in [tuple,list]:

            retorno = {}

            for cod in cods:

                if str(cod) in sn:
                    retorno[cod] = True
                else:
                    retorno[cod] = False

            return retorno


        else:

            if str(cods) in sn:
                return True

            else:
                return False

    def getSocios(self,cod):

        sociosEmp = self.dfSocios[self.dfSocios['cod'] == cod].copy()
        sociosEmp['resp_leg'] = sociosEmp['cpf'] == sociosEmp['cpf_leg_emp']

        sociosEmp.drop_duplicates(subset='cpf',inplace=True)

        socios = sociosEmp[['nome','cpf','resp_leg']].to_dict(orient='records')

        return socios
