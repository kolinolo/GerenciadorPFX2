def deColorLen(texto):
    if len(texto) == 0:
        return 0

    if texto[0] == '\x1b':
        texto = texto[5:-5]

    return len(texto)




class configCentralizar:

    def __init__(self, MX: int, borda: str,skipRow:bool = False):
        self.MX = MX
        self.borda = borda
        self.skipRow = skipRow

    def centralizar(self, texto: str, ):
        tamanhoTexto = deColorLen(texto)
        if tamanhoTexto == 0:

            texto = self.borda
        fix = 0
        if tamanhoTexto % 2 != 0: fix = 1

        if self.skipRow:
            sk = '\n'
        else:
            sk = ''

        espacos = int((self.MX - tamanhoTexto) / 2)
        if len(self.borda) > 1:
            print(f"{sk}{(self.borda * espacos)[:espacos]} {texto} {(self.borda * espacos)[espacos - fix:]}{sk}")

        else:
            print(f"{sk}{self.borda * espacos} {texto} {self.borda * (espacos + fix)}{sk}")


class configColorizar:
    def __init__(self, cor: str, autoPrint: bool = False,skipRow:bool = False):
        if cor not in ['rosa', 'azul', 'verde', 'amarelo', 'vermelho', 'clear']:
            raise CorInexistente

        self.cor = cor
        self.autoPrint = autoPrint
        self.skipRow = skipRow

    def colorizar(self, texto):
        cores = {'rosa': '\033[95m', 'azul': '\033[94m', 'verde': '\033[92m', 'amarelo': '\033[93m',
                 'vermelho': '\033[91m',
                 'clear': '\033[0m', }

        if self.skipRow:
            sk = '\n'
        else:
            sk = ''

        if self.cor not in cores:
            raise CorInexistente(f"Cor {self.cor} invalida")

        if self.autoPrint:
            print(f"{sk}{cores[self.cor]}{texto}{cores["clear"]}{sk}")

            return ''

        else:
            return f"{sk}{cores[self.cor]}{texto}{cores["clear"]}{sk}"


class CorInexistente(Exception):
    pass

