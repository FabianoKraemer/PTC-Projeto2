#!/usr/bin/python3
# -*- coding: utf-8 -*

# Dec 0 = 0000 0000  Data + sequencia 0
# Dec 8 = 0000 1000  Data + sequencia 1

# DEC 128 = 1000 0000  ACK + sequencia 0
# DEC 136 = 1000 1000  ACK + sequencia 1

from protocolo import Subcamada
from enum import Enum


class Arq(Subcamada):

    def __init__(self, timeout):
        Subcamada.__init__(self, None, timeout)
        self.enable_timeout() # Ativa o timeout
        self.Estados = Enum('Estados', 'ocioso espera') # Somente dois estados, conforme MEF montada em aula
        self.estado = self.Estados.ocioso # Inicia no estado ocioso
        self.Eventos = Enum('Eventos', 'ack dado payload timeout')
        self.buffer = bytearray()
        self.Ack_recebido = False
        self.seq_Recebe = False # Inicia como false, sinalizando primeiro recebimento
        self.seq_Envio = False # Inicia como false, sinalizando primeiro envio
        self.n_tentativas = 0 # Número de tentativas de reenvio, com máximo de 5 tentativas
        self.dado = bytearray()
        self.env_dado = bytearray()

    def envia(self, payload):
        self.evento = self.Eventos.payload # Armazena os dados enviados da camada superior no payload
        self.buffer = payload # Adiciona no buffer os dados de payload do quadro, a direita do controle, RESERVADO + ID Proto
        #self.ctrlbyte = payload[0:1] # Adiciona os dados do controle do quadro
        self.handle()

    def recebe(self, dados: bytes):
        self.dado = dados
        ctrl_int = int.from_bytes(dados[0:1], "big") # Transforma em decimal pra fazer a manipulação
        if(ctrl_int == 128 or ctrl_int == 136):
            self.evento = self.Eventos.ack
            self.buffer == bytearray()                                
        else:
            if(ctrl_int == 8):
                self.seq_Recebe = 0x08
            else:
                self.seq_Recebe = 0x00
            self.evento = self.Eventos.dado    
        self.handle()

    def handle(self):
        if (self.estado == self.Estados.ocioso):
            #print('estado ocioso')
            if(self.evento == self.Eventos.payload):
                self.estado = self.Estados.espera
                self.envia_quadro()
                self.reload_timeout()
                self.enable_timeout()
            elif(self.evento == self.Eventos.dado):
                self.envia_ack()  
                #print("dados recebidos: ", self.dados.decode('utf8'))  
                self.upper.recebe(bytes(self.dado))                                 
        if (self.estado == self.Estados.espera):
            #print('estado recebendo')
            if(self.evento == self.Eventos.ack):
                self.disable_timeout() # Recebeu um ACK, timeout desativado
                self.estado = self.Estados.ocioso # Volta pro estado ocioso
                self.upper.recebe(bytes(self.dado)) # Sobe pra camada da aplicação
            elif(self.evento == self.Eventos.dado):                       
                self.upper.recebe(bytes(self.dado))
                self.envia_ack() 
            elif(self.evento == self.Eventos.timeout):
                print('Erro, tentando reenviar a msg')  
                self.n_tentativas += 1
                if(self.n_tentativas <= 4): # tenta enviar 5 vezes
                    self.envia_quadro()
                    self.reload_timeout()
                else:
                    print('Tentou reenviar 5 vezes e não conseguiu, retornando ao estado ocioso')
                    self.estado = self.Estados.ocioso # Volta para o estado ocioso após tentar enviar por 5 vezes
                    self.n_tentativas = 0
                    self.disable_timeout()            

    def handle_timeout(self):
        #print('ARQ: Timeout')
        self.evento = self.Eventos.timeout
        self.handle()

    def envia_quadro(self):
        if(self.seq_Envio): # Se verdadeiro é o "2o envio de dado", sequencia 1, e do tipo dado
            controle = b'\x08' # 0000 1000
        else: # Se seq_Envio é falso, é sequência 0 do controle, e dado
            controle = b'\x00' # 0000 0000
        self.seq_Envio = not self.seq_Envio # Inverte a sequencia de envio sinalizando novo quadro
        self.env_dado = controle + b'\x00' + b'\x00' + self.buffer
        self.lower.envia(self.env_dado)

    def envia_ack(self):    
        if(self.seq_Recebe): # Dec 0 = 0000 0000  Data + sequencia 0
            ctrl = b'\x88' # DEC 128 = 1000 0000  ACK + sequencia 0
            print('Enviando ACK 1') 
        else:  # Dec 8 = 0000 1000  Data + sequencia 1
            ctrl = b'\x80' # DEC 136 = 1000 1000  ACK + sequencia 1
            print('Enviando ACK 0')

        self.lower.envia(ctrl + b'\x00' + b'\x00') # Envia o byte de controle + Reservado + ID Proto (Payload vazio)
