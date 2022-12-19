import poller
import sys
from enquadramento import Enquadramento
from serial import Serial
from aplicacao import Aplicacao
from arq import Arq

Timeout = 15  # 15 segundos

# nome da porta serial informada como primeiro argumento
# de linha de comando
try:
    porta = Serial(sys.argv[1])
except:
    print('Erro ao tentar conectar na porta serial: %s porta_serial' %
          sys.argv[0])
    sys.exit(0)

#p = Serial(porta, 9600, Timeout)
#porta_tx = "/dev/pts/6"  # porta do serialEMU usada para TX
#porta_rx = "/dev/pts/7"  # porta do serialEMU usada para RX

# cria objeto Enquadramento
enq = Enquadramento(porta, Timeout)

# Cria objeto Aplicacao
app = Aplicacao()

# Cria o arq com timeout de 3s
arq = Arq(3) 

# Conecta as subcamadas
# Deve ser feito a partir da subcamada inferior
enq.conecta(arq)

arq.conecta(app)

# Cria o Poller e registra os callbacks
sched = poller.Poller()
sched.adiciona(enq)
sched.adiciona(arq)
sched.adiciona(app)

# Entrega o controle ao Poller
sched.despache()
