class EnvironmentNotSetError(Exception):

    def __init__(self, cwd):

        super().__init__(f"as variáveis do ambiente não foram setadas no em : {cwd}")

    pass


class CNPJInvalido(Exception):

    def __init__(self,pj):

        super().__init__(f"'{pj}' não é um cnpj, pf ou raiz Válido")

    pass