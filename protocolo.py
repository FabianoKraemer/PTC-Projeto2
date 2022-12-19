from poller import Callback

class Subcamada(Callback):
    def __init__(self, dev, timeout:int = 0):
        Callback.__init__(self, dev, timeout)
        self.upper = None
        self.lower = None

    def conecta(self, camada):
        if not isinstance(camada, Subcamada):
            raise ValueError('Deve ser uma instância de Subcamada')
        self.upper = camada
        camada.lower = self

    def envia(self, dados:bytes):
        raise NotImplementedError('metodo abstrato')
    
    def recebe(self, dados:bytes):
        raise NotImplementedError('metodo abstrato')