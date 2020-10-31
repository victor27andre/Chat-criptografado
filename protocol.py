class ProtocolMessage:

    def __init__(self, msgType='', msgLength=0, msgValue=''):
        self.msgType = msgType
        self.msgLength = msgLength
        self.msgValue = msgValue

    def encode(self):

        # TODO fazer criptografia aqui ó

        return f'{self.msgType} {self.msgValue}'.encode('utf8')

    def decode(self, data):
        msg = data.decode('utf-8')

        # TODO fazer descriptografia aqui ó

        # self.msgType = msg[0:4].strip()
        self.msgType = msg[0:4]
        self.msgLength = len(data)
        self.msgValue = msg[5:]

    def __repr__(self):
        return f'{self.msgType} {self.msgValue}'


def read_incoming(received):
    x = ProtocolMessage()
    x.decode(received)
    return x


def prepare_to_send(command, message=''):
    if command.lower() in ['retr', 'clos']:
        x = ProtocolMessage(command.lower().ljust(4), 5)
    else:
        x = ProtocolMessage(command.lower().ljust(4), 5 + len(message.encode('utf-8')), message)
    return x

