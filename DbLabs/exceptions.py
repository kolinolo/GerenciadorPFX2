class EnvironmentNotSetError(Exception):

    def __init__(self, cwd):

        super().__init__(f"as variáveis do ambiente não foram setadas no em : {cwd}")

    pass