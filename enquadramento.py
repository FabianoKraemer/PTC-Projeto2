from enum import Enum
from protocolo import Subcamada
import crc

# usando como base coisas desenvolvidas nos semestres anteriores
class Enquadramento(Subcamada):

    def __init__(self, serial, timeout):
        Subcamada.__init__(self, serial, timeout)
        self.dev = serial  # dev: este atributo mantém uma referência à porta serial       
        self.Estados = Enum('Estados', 'ocioso init rx esc') # Estados possíveis da ME
        self.estado = self.Estados.ocioso  # Estado inicial da MEF
        self.buffer = bytearray()  # Buffer que vai armazenar os dados lidos da serial
        self.n_bytes = 0
        self.ser = serial  # objeto serial para conexão com a interface serial do SerialEMU
        self.enable_timeout()

    def envia(self, data):
        final_data = bytearray()
        fcs = crc.CRC16(data)
        msg = fcs.gen_crc()
        #print('Mensagem com CRC: ', msg)
        #dados_digitados = data.encode('utf8')
        #dados_digitados = data.encode('ascii')

        # loop para fazer o enquadramento e substituição dos bytes
        for i in range(0, len(msg)):
            if ((msg[i] == 0x7E) or (msg[i] == 0x7D)):
                trans_byte = bytes([msg[i] ^ 0x20])
                final_data = final_data + b'\x7D' + trans_byte
            else:
                final_data = final_data + bytes([msg[i]])
        final_data = b'\x7E' + final_data + b'\x7E'

        self.ser.write(final_data)  # envia os dados para a serial
        #print('Enviando enquadrado: ', final_data)

    def recebe(self):
        dado_recebido = self.ser.read(1)
        if (dado_recebido == bytearray()):
            return False
        if (self.handle_dado(dado_recebido, self.estado) == True):
            fcs = crc.CRC16('')  # cria o objeto vazio
            fcs.clear()  # limpando
            # adiciona os dados recebidos para checagem do CRC
            fcs.update(self.buffer)
            if (fcs.check_crc() == True):  # se o CRC estiver correto, vai para as etapas abaixo
                #print('Teste buffer com CRC correto: ', self.buffer)
                # remove os dois ultimos bytes, pois são os LSB e MSB do CRC
                self.buffer = self.buffer[0:-2]
                return True
            if (fcs.check_crc() == False):
                print('Deu erro no CRC recebido')
                self.estado = self.Estados.ocioso
                return False

    def handle(self):
        if self.recebe() == True:
            self.upper.recebe(bytes(self.buffer))
            self.buffer.clear() # Limpando o buffer pra não acumular

    def handle_dado(self, byte, estado):
        if (self.estado == self.Estados.ocioso):
            if (byte == b'\x7E'):
                self.n_bytes = 0
                self.estado = self.Estados.init
        if (self.estado == self.Estados.init):
            if (byte == b'\x7E'):
                self.buffer.clear()
                return False
            if (byte == b'\x7D'):
                self.estado = self.Estados.esc
                return False
            else:
                self.buffer += byte
                self.estado = self.Estados.rx
                self.n_bytes += 1
                return False
        if (self.estado == self.Estados.rx):
            if (byte == b'\x7E'):
                self.estado = self.Estados.ocioso
                return True
            if (byte == b'\x7D'):
                self.estado = self.Estados.esc
                return False
            else:
                self.buffer += byte
                self.n_bytes += 1
                return False
        if (self.estado == self.Estados.esc):
            if (byte == b'\x7E'):
                self.buffer = bytearray()
                self.estado = self.Estados.ocioso
            else:
                byte = byte[0] ^ 0x20
                self.buffer += bytes([byte])
                self.estado = self.Estados.rx
            return False

    def handle_timeout(self):
        # Limpa o buffer se ocorrer timeout
        self.buffer.clear()
        #print('Timeout do enquadramento')
