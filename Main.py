import time

from sqlalchemy import create_engine
import DbLabs # instalado no UV do projeto, faz referência ao DbLabs na pasta Libs desse pc
from PrintTool import printTool
import pandas as pd
from datetime import datetime
import os

from Objetos.infoCert import certificadoLD
from moveDescarta import descartaValidade, descartaNaoCliente, renomeia

sqlEngine = create_engine('postgresql://Ethos:ethos789@192.168.2.10:1611/certificados')
siegEngine = create_engine('postgresql://Ethos:ethos789@192.168.2.10:1611/Sieg')

pd.set_option('future.no_silent_downcasting', True)

os.system('cls' if os.name == 'nt' else 'clear')
vermelho = printTool.configColorizar('vermelho', autoPrint=True).colorizar
verde = printTool.configColorizar('verde', autoPrint=True).colorizar
amarelo = printTool.configColorizar('amarelo', autoPrint=True).colorizar
roxo = printTool.configColorizar('rosa', autoPrint=False).colorizar

hoje = datetime.today().date()

etapa = printTool.configCentralizar(100, '~', skipRow=True).centralizar
separador = printTool.configCentralizar(100, '-', skipRow=True).centralizar

bd = DbLabs.buscaDominio()

base = pd.read_sql('''
                            SELECT cod, base.razao, cnpj
                            FROM relatorios.base
                                     LEFT JOIN relatorios.ret ON ret.razao = base.razao
                            
                            WHERE (ret.matriz IS NULL or ret.matriz = base.cod) 
                                      AND status != 'I' and tipo_cert != 'A3';''', siegEngine).astype({'cod':int})


socios = bd.querryToDF("""
                select inscricao as cpf
                ,e.codi_emp as cod,e.razao_emp as razao from bethadba.gequadrosocietario_socios s join
    bethadba.gesocios s1 on s1.i_socio = s.i_socio
    left join bethadba.geempre e on s.codi_emp = e.codi_emp
               """).astype({'cod':int},errors='ignore')


# DFs
socios.sort_values('cod',inplace=True)
socios.drop_duplicates(subset=['cpf'],keep='first',inplace=True)

empresas = bd.querryToDF("""select razao_emp as razao,
                                   codi_emp as cod,
                                   stat_emp as status,
                                   cgce_emp as cnpj
                                   from bethadba.geempre""").astype({'cod':int})
empresas.drop_duplicates(subset=['cnpj'],keep='last',inplace=True)

estatisticas = {'Empresas validas totais': len(base)}

erros = pd.DataFrame(columns={'original':str,'erro':str,'origem':str})


# Funções etapas

def segundaChanceNClientePJ():

    diretorio = r'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CNPJ\Inválidos\Não clientes'
    reviveDir = r'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CNPJ'

    certs = []
    for arquivo in os.listdir(diretorio):

        if arquivo.endswith(('pfx', 'p12')):
            certs.append(arquivo)


    col = {
        'id': int,
        'original': str,
        'senha': str,
        'validade': datetime.date,
        'cnpj': datetime.date,
        'alterada': bool}

    pj = pd.DataFrame(columns=col)

    for cert in certs:

        try:
            leitura = certificadoLD(cert, diretorio)

            pj.loc[len(pj)] = [len(pj),
                               cert,
                               leitura.senha,
                               leitura.validade,
                               leitura.PF_PJ,
                               False
                               ]



        except Exception as e:

            print(f'Exceção na leitura do certificado do não cliente {cert}: {e}')

    pjs = pj.merge(empresas, how='left', on='cnpj')
    pjs.fillna({'razao': 'Não Cliente', 'cod': '00', 'status': 'I'}, inplace=True)

    # Volta para pasta dos válidos
    for reviver in pjs[pjs['status'] != 'I']['original'].tolist():
        os.rename(fr'{diretorio}\{reviver}',
                  fr'{reviveDir}\{reviver}')
        verde(f"cliente recuperado {reviver}")

    # Descarta expirados
    for expirado in pjs[(pjs['validade'] < hoje) & (pjs['status'] == 'I')].index:
        descartaValidade(pjs.iloc[expirado],'PJ',subpasta='Inválidos\\Não clientes\\')


    del pjs, pj

def segundaChanceNClientePF():
    diretorio = r'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CPF\Não Cliente'
    reviveDir = r'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CPF'

    certs = []
    for arquivo in os.listdir(diretorio):

        if arquivo.endswith(('pfx', 'p12')):
            certs.append(arquivo)

    pf = pd.DataFrame(columns={
        'id': int,
        'original': str,
        'nome': str,
        'cpf': str,
        'senha': str,
        'validade': datetime.date,
        'alterada': bool,
    })

    for cert in certs:

        try:
            leitura = certificadoLD(cert, diretorio)

            pf.loc[len(pf)] = [len(pf),
                               cert,
                               leitura.razao,
                               leitura.PF_PJ,
                               leitura.senha,
                               leitura.validade,
                               False
                               ]



        except Exception as e:

            print(f'Exceção na leitura do certificado do não cliente {cert}: {e}')

    pfs = pf.merge(socios, how='left', on='cpf')
    pfs.fillna({'razao': 'Não Cliente', 'cod': '00'}, inplace=True)

    # Volta para pasta dos válidos
    for reviver in pfs[pfs['razao'] != 'Não Cliente']['original'].tolist():
        os.rename(fr'{diretorio}\{reviver}',
                  fr'{reviveDir}\{reviver}')
        verde(f"cliente recuperado {reviver}")

    for expirado in pfs[(pfs['validade'] < hoje) & (pfs['razao'] == 'Não Cliente')].index:
        descartaValidade(pfs.iloc[expirado],'PF',subpasta='Não Cliente\\')


def inicializarPF():
    certs = []
    raiz = fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CPF'

    pf = pd.DataFrame(columns={
        'id': int,
        'original': str,
        'nome': str,
        'cpf': str,
        'senha': str,
        'validade': datetime.date,
        'alterada': bool,
    })


    diretorio = os.listdir(raiz)
    for arquivo in diretorio:
        if arquivo.endswith(('pfx','p12')):
            certs.append(arquivo)

    for cert in certs:

        try:

            leitura = certificadoLD(cert,raiz)

            if len(leitura.PF_PJ) == 14:
                erros.loc[len(erros)] = [cert, 'Pasta incorreta: PJ em PF','PF']
                continue

            pf.loc[len(pf)] = [len(pf),
                               cert,
                               leitura.razao,
                               leitura.PF_PJ,
                               leitura.senha,
                               leitura.validade,
                               False
                               ]



        except IndexError as e:

            erros.loc[len(erros)] = [cert,'Formatação ou senha incorreta','PF']
            print(f'Erro ao ler o arquivo: {cert}')

        except TypeError as e:

            erros.loc[len(erros)] = [cert, 'Falha na leitura','PF']
            print(f'Erro ao ler o arquivo: {cert}')

        #Identifica clientes

    pfs = pf.merge(socios, how='left', on='cpf')
    pfs.fillna({'razao': 'Não Cliente', 'cod': '00'}, inplace=True)

    estatisticas['totalPF'] = len(pfs)
    amarelo(f'{estatisticas['totalPF']} Certificador processados')

    return pfs


def inicializarPJ():

    certs = []
    raiz = fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CNPJ'
    diretorio = os.listdir(raiz)

    pj = pd.DataFrame(columns={
                    'id':int,
                    'original': str,
                    'senha': str,
                    'validade': datetime.date,
                    'cnpj': datetime.date,
                    'alterada': bool})

    for arquivo in diretorio:
        if arquivo.endswith(('pfx','p12')):
            certs.append(arquivo)

    for cert in certs:

        try:

            leitura = certificadoLD(cert,raiz)

            if len(leitura.PF_PJ) == 11:
                erros.loc[len(erros)] = [cert, 'Pasta incorreta: PF em PJ','PJ']
                continue

            pj.loc[len(pj)] = [len(pj),
                               cert,
                               leitura.senha,
                               leitura.validade,
                               leitura.PF_PJ,
                               False
                               ]

        except IndexError as e:

            erros.loc[len(erros)] = [cert, 'Formatação ou senha incorreta','PJ']
            print(f'Erro ao ler o arquivo: {cert}')

        except TypeError as e:

            erros.loc[len(erros)] = [cert, 'Falha na leitura','PJ']
            print(f'Erro ao ler o arquivo: {cert}')

    pjs = pj.merge(empresas, how='left', on='cnpj')
    pjs.fillna({'razao': 'Não Cliente', 'cod': '00','status':'I'},inplace=True)

    estatisticas['totalPJ'] = len(pjs)
    amarelo(f'{estatisticas['totalPJ']} Certificador processados')
    return pjs




try:

    etapa(roxo('Verificando pasta não cliente CNPJ'))
    segundaChanceNClientePJ()

    etapa(roxo('Verificando pasta não cliente CNPJ'))
    segundaChanceNClientePF()

except Exception as e:
    print(e)

etapa(roxo('Lendo PFX CPF'))

pf = inicializarPF()

etapa(roxo('Lendo PFX CNPJ'))
pj = inicializarPJ()

pf = pf.set_index('id', drop=False)
pf = pf.set_index('id', drop=False)


etapa(roxo('Conferindo nome do arquivo CPF'))
for i in range(len(pf)):

    linhaA = pf.iloc[i]

    nome = linhaA['nome']
    senha = linhaA['senha']
    validade = linhaA['validade'].strftime("%d.%m.%Y")
    razao = linhaA['razao']
    tipo = linhaA['original'][-4:]

    if linhaA['original'] != f"{nome} - {senha} - {validade} - {razao}{tipo}":
        pf.loc[linhaA['id'],'alterada'] = True

    del razao, senha, validade, nome, tipo,i


etapa(roxo('Conferindo nome do arquivo CNPJ'))
for i in range(len(pj)):

    linhaA = pj.iloc[i]

    razao = linhaA['razao']
    senha = linhaA['senha']
    validade = linhaA['validade'].strftime("%d.%m.%Y")
    cod = int(linhaA['cod'])

    tipo = linhaA['original'][-4:]

    if linhaA['original'] != f"{razao} - {senha} - {validade} - {cod}{tipo}":
        pj.loc[linhaA['id'],'alterada'] = True

    del razao, senha, validade, cod, tipo,i



#finalizando corretos:

etapa(roxo('Transferindo inválidos e renomeando arquivos CPF'))
for i in range(len(pf)): # CPF

    linhaA = pf.iloc[i]

    if linhaA['razao'] == 'Não Cliente':
        descartaNaoCliente(linhaA, 'PF')
        continue

    if linhaA['validade'] < hoje:
        descartaValidade(linhaA, 'PF')
        continue


    if linhaA['alterada']:
        renomeia(linhaA,'PF')
        continue


etapa(roxo('Transferindo inválidos e renomeando arquivos CNPJ'))
for i in range(len(pj)): # CNPJ

    linhaA = pj.iloc[i]




    if linhaA['razao'] == 'Não Cliente' or linhaA['status'] == 'I':
        descartaNaoCliente(linhaA, 'PJ')
        continue

    if linhaA['validade'] < hoje:

        try:
            descartaValidade(linhaA, 'PJ')

        except FileNotFoundError as e:
            print(e)
            continue


    if pj.iloc[i]['alterada']:
        renomeia(linhaA,'PJ')
        continue


etapa(roxo('Tratando erros'))

for i in range(len(erros)):

    linhaA = erros.iloc[i]

    if linhaA['origem'] == 'PF':
        R = fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CPF'

    else:
        R = fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CNPJ'

    original = linhaA['original']


    match linhaA['erro']:


        case 'Formatação ou senha incorreta':

            try:
                os.rename(
                    fr"{R}\{original}",
                    fr"{R}\Inválidos\Senha Incorreta\{original}"
                )

                amarelo(f'{original} --> formatação ou senha incorreta')

            except Exception as e:
                print(e)

        case 'Falha na leitura':

            try:
                os.rename(
                    fr"{R}\{original}",
                    fr"{R}\Inválidos\Senha Incorreta\{original}"
                )

                amarelo(f'{original} --> Senha Incorreta')

            except Exception as e:
                print(e)

        case "Pasta incorreta: PJ em PF":
            try:
                os.rename(
                    fr"{R}\{original}",
                    fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CNPJ\{original}'
                )

                verde(f'Certificado transferido: {original} -> E-CNPJ')

            except Exception as e:
                print(e)

        case "Pasta incorreta: PF em PJ":
            try:
                os.rename(
                    fr"{R}\{original}",
                    fr'\\servidor\Ethos\SERVIDOR\Certificados digitais\E-CPF\{original}'
                )

                verde(f'Certificado transferido: {original} -> E-CPF')

            except Exception as e:
                print(e)

    del original,R, linhaA


etapa(roxo('Processo finalizado'))
separador('')
etapa(roxo('Relatórios'))

socios = bd.querryToDF("""
                select  s1.nome ,s1.inscricao as cpf,e.codi_emp as cod,
        e.razao_emp as razao, e.rleg_emp
from bethadba.gequadrosocietario_socios s join bethadba.gesocios s1
    on s1.i_socio = s.i_socio

left join bethadba.geempre e on s.codi_emp = e.codi_emp
where e.stat_emp != 'I' and data_saida is NULL
order by s1.nome""").astype({'cod':int},errors='ignore')

socios['responsavel'] = socios['rleg_emp'] == socios['nome']
socios = socios[socios['cpf'].str.len() == 11]

pfValidos = pf[pf['validade'] > hoje][['cpf']].reset_index(drop=True)
pfValidos['valido'] = True

socios = pd.merge(socios,pfValidos,on='cpf',how='left')
socios.fillna({'valido':False},inplace=True)

rSocios = socios[['nome','cpf','valido','responsavel','cod','razao'
                  ]].rename(columns={'valido':'certificado'})

pjValidos = pj[pj['validade'] > hoje][['cod','validade']].astype({'cod': int})
pjValidos['valido'] = True


empresas = pd.merge(base,pjValidos,on='cod',how='left')
empresas.drop_duplicates(subset=['cnpj'],keep='last',inplace=True)
empresas.fillna({'valido':False},inplace=True)




try:

    rSocios.to_sql('socios',
                   sqlEngine,
                   if_exists='replace')
    etapa(roxo('Sócios Atualizado'))


    empresas.to_sql('clientes',
                    sqlEngine,
                    if_exists='replace')
    etapa(roxo('Clientes Atualizado'))


    estatisticas['Socios com certificado'] = len(rSocios[rSocios['certificado'] == True])
    estatisticas['Socios sem certificado'] = len(rSocios[rSocios['certificado'] == False])

    estatisticas['Empresas com certificado'] = len(empresas[empresas['valido'] == True])
    estatisticas['Empresas sem certificado'] = len(empresas[empresas['valido'] == False])

    estatisticas['erros'] = len(erros)


except Exception as e:
    print(e)

print(estatisticas)

time.sleep(10)

