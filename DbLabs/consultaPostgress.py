import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .exceptions import EnvironmentNotSetError
from dotenv import load_dotenv

import os

if 'DbLabs.env' not in os.listdir(os.getcwd()):
    print('O ambiente do Dblabs NÃO foi setado')

    raise EnvironmentNotSetError(os.getcwd())

load_dotenv(r"DbLabs.env")

UID = os.getenv('UIDPG')
PWD = str(os.getenv('PWDPG'))
PORTA = os.getenv('PORTAPG')
SERVIDOR = os.getenv('SERVIDOR')
conexao = f'postgresql://{UID}:{PWD}@{SERVIDOR}:{PORTA}/'


engine = create_engine(conexao)




def getEngine(bd):

    if bd != '' and bd is not None:

        return create_engine(f'{conexao}{bd}')

    else:

        return engine


def getClientesBase():
    """ Clientes não ret, ativos """

    localEngine = getEngine('Sieg')

    retorno = pd.read_sql('''

                          select cod
                          from relatorios.base
                                   left join relatorios.ret on ret.razao = base.razao
                          where ret is null
                            and status != 'I';

                          ''', localEngine).astype(str)

    lista = retorno['cod'].tolist()

    return lista


def querryToDFPG(query: str, bd=''):

    localEngine = getEngine(bd)

    retorno = pd.read_sql(query, localEngine)

    return retorno


def executaComando(sql, bd=None):
    if bd != '':

        localEngine = create_engine(f'{conexao}/{bd}')

    else:
        localEngine = engine

    Session = sessionmaker(bind=localEngine)
    session = Session()

    try:
        sql_query = text(sql)
        session.execute(sql_query)
        session.commit()

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")

    finally:
        session.close()

    pass


def appendDF(tabela,df,  bd='', unique=False):


    colunas = df.columns.tolist()
    localEngine = getEngine(bd)

    Session = sessionmaker(bind=localEngine)
    session = Session()

    try:


        sql = text(f"""
        
                INSERT INTO {tabela} ({','.join(colunas)})
                VALUES ({','.join(':' + c for c in colunas)})
                {'ON CONFLICT DO NOTHING' if unique else ''}
                    
                    """)


        dados = df.to_dict(orient='records')

        session.execute(sql, dados)

        session.commit()


    except Exception as e:
        print(e)
        session.rollback()

    session.close()

def lastID(tabela:str,coluna:str ='id'):
    """Retorna o maior valor de uma coluna, usado para auto incrementar"""

    df = querryToDFPG(f'select {coluna} from {tabela}')

    return df[coluna].max()


