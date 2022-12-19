#!/usr/bin/python3

from serial import Serial
from enquadramento import Enquadramento
import sys
from binascii import unhexlify
import poller

'''
try:
    porta = sys.argv[1]
except:
    print('Uso: %s porta_serial' % sys.argv[0])
    sys.exit(0)
'''
porta_rx = "/dev/pts/6"

try:
    p = Serial(porta_rx, 9600, timeout=10)
except Exception as e:
    print('Não conseguiu acessar a porta serial', e)
    sys.exit(0)


#msg = 0

# criando objeto do enquadramento com a respectiva porta da seria

enq = Enquadramento(p, 10)

while (enq.buffer != 'sair'):
    enq.recebe()


'''
while (msg != "sair"):
    try:
        p = Serial(porta_rx, 9600, timeout=3)
    except Exception as e:
        print('Não conseguiu acessar a porta serial', e)
        sys.exit(0)

    # recebe até 128 caracteres
    msg = p.read(128)  # mensagem recebida no formato byte octeto
    # decodificando para formato ascii, para tirar o b''
    msg = msg.decode('ascii')
    if (len(msg) > 0):
        print('Recebeu: ', msg)
        print(' | Tamanho da mensagem:', len(msg))

'''

sys.exit(0)
