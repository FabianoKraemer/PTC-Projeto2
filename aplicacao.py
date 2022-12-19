import sys
from protocolo import Subcamada


class Aplicacao(Subcamada):

    def __init__(self):
        Subcamada.__init__(self, sys.stdin)

    def recebe(self, dados: bytes):
        # mostra na tela os dados recebidos da subcamada inferior
        #print('Dados recebidos (payload): ', dados.decode('utf8'))       
        byte_controle = dados[0:1]
        dados_recebidos = dados[3:]
        ctrl_int = int.from_bytes(byte_controle, "big") 
        print('Byte de controle: ', ctrl_int, '| quadro recebido: ', dados)  

        if(ctrl_int == 0):
            print('Dados sequência 0 recebido: ', dados_recebidos)               
        elif(ctrl_int == 8):
            print('Dados sequência 1 recebido', dados_recebidos)           
        elif(ctrl_int == 128):
            print('ACK 0 recebido') 
        elif(ctrl_int == 136):
            print('ACK 1 recebido')                                       
        else:
            print('Dados corrompidos')   
        print('-----------------------------------------------')
        #self.desmonta_quadro(dados)
        # self.desmonta_quadro(self, dados)

    def handle(self):
        # lê uma linha do teclado
        dados = sys.stdin.readline()

        # converte para bytes, necessário somente
        # nesta aplicação de teste, que lê do terminal
        dados = dados.encode('utf8')

        # monta o quadro
        self.monta_quadro(dados)

    def monta_quadro(self, dados):
        self.lower.envia(dados)
