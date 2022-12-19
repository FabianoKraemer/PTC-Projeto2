#!/usr/bin/python3
import sys
from serial import Serial
from enquadramento import Enquadramento
from binascii import unhexlify
import poller


# comando para configurar algumas coisas do serial emu: sudo minicom -s

porta_tx = "/dev/pts/5"  # porta do serialEMU usada para TX

# tentando se conectar na porta serial
try:
    p = Serial(porta_tx, 9600, timeout=10)
except Exception as e:
    print('Não conseguiu acessar a porta serial', e)
    sys.exit(0)

# criando objeto do enquadramento com a respectiva porta da serial
enq = Enquadramento(p, 10)
# enq.conecta()
sched = poller.Poller()
sched.adiciona(enq)
# implementar a verificação do tamanho dos dados, <= 1024

controle_while = 0
while (controle_while != "sair"):
    controle_while = input("Digite algo:\n")
    enq.envia(controle_while)
    #n = p.write(controle_while.encode('ascii'))
    #print('Enviou %d bytes' % n)

#msg = 'um teste ...\r\n'

#input('Digite ENTER para terminar:')

sys.exit(0)
