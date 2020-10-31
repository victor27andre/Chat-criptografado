import protocol as cp

from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM

# erro 001 = usuario nao existente
# erro 002 = senha errada
# erro 003 = sem usuario para checar senha
# erro 004 = usuario nao logado
# erro 005 = usuario nao encontrado

class ServerHandler(Thread):

    def __init__(self, host, port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.connections = []
        self.active = True
        self.users = {'bruno': '5',
                      'joao': '4',
                      'maria': '3',
                      'rafael': '1',
                      'rubens': '2'}

    def stop(self):
        self.active = False

    def check_username(self, username):
        if username in self.users.keys():
            return True
        else:
            return False

    def check_password(self, username, password):
        if self.users[username] == password:
            return True
        else:
            return False

    def get_user_from_addr(self, addr):
        for client in self.connections:
            if client.addr == addr:
                return client.username
        return None

    def brod(self, msg, from_addr):
        for client in self.connections:
            if client.addr != from_addr:
                client.conn.sendall(msg.encode())

    def retrive_all_connections(self, from_addr):
        data = ''
        for client in self.connections:
            if client.addr != from_addr:
                data += f'{client.username} : {client.addr}\n'
        return data


    def close_conn(self):
        return


    def priv(self, data, from_user):
        to_user = data.msgValue.split(' ')[0]
        for client in self.connections:
            if client.username == to_user:
                msg = cp.prepare_to_send('priv', f'({from_user}): {data.msgValue.split(" ")[1]}')
                client.conn.sendall(msg.encode())
                return True
        return False  # nao achou para quem mandar

    def run(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(5)

            while self.active:
                print(f'Waiting for new connections...')

                conn, addr = s.accept()

                ch = ConnectionHandler(conn, addr, self)
                self.connections.append(ch)
                ch.start()

            # Adicionar o código solicitando o fechamento das conexões com os clientes!


class ConnectionHandler(Thread):

    def __init__(self, conn, addr, callback):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.callback = callback
        self.active = True
        self.logged = False
        self.username = ''
        self.password = ''
        self.tent = 0

    def close_conn(self):
        return


    def run(self):
        print(f'O cliente {self.addr} foi conectado!\n')

        with self.conn:
            while self.active:
                data = self.conn.recv(1024)  # TODO checar que isso aqui pode dar merda lendo só 4 em vez de 5
                data_rec = cp.read_incoming(data)

                if data_rec.msgType == 'user':
                    if self.callback.check_username(data_rec.msgValue):
                        self.username = data_rec.msgValue
                        print(f'O cliente {self.addr} conectou como {self.username}!\n')
                        response = cp.prepare_to_send('ok')
                        self.conn.sendall(response.encode())
                    else:
                        response = cp.prepare_to_send('err', message='001')  # usuario nao existente
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'pass':
                    if self.username == '':
                        response = cp.prepare_to_send('err', message='003')  # nao tinha usuario ainda
                        self.conn.sendall(response.encode())

                    if self.callback.check_password(self.username, data_rec.msgValue):
                        self.password = data_rec.msgValue
                        self.logged = True
                        print(f'O cliente {self.addr} conectado como {self.username} logou com sucesso!\n')
                        response = cp.prepare_to_send('ok')
                        self.conn.sendall(response.encode())
                    else:
                        response = cp.prepare_to_send('err', message='002')  # senha errada
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'mesg':
                    if self.logged:
                        broad_send = cp.prepare_to_send('brod', self.username + ' ' + data_rec.msgValue)
                        self.callback.brod(broad_send, self.addr)
                        print(f'O cliente {self.addr} mandou um texto broadcast : {data_rec.msgValue}\n')
                    else:
                        response = cp.prepare_to_send('err', message='004')  # usuario nao logado
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'retr':
                    if self.logged:
                        msg = self.callback.retrive_all_connections(self.addr)
                        response = cp.prepare_to_send('ok', message=msg)
                        self.conn.sendall(response.encode())
                    else:
                        response = cp.prepare_to_send('err', message='004')  # usuario nao logado
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'priv':
                    if self.logged:
                        if self.callback.priv(data_rec, self.username):
                            pass
                        else:
                            response = cp.prepare_to_send('err', message='005')  # usuario nao encontrado
                            self.conn.sendall(response.encode())
                    else:
                        response = cp.prepare_to_send('err', message='004')  # usuario nao logado
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'brod':
                    if self.logged:
                        ...
                    else:
                        response = cp.prepare_to_send('err', message='004')  # usuario nao logado
                        self.conn.sendall(response.encode())

                elif data_rec.msgType == 'clos':
                    print(f'O cliente {self.addr} conectado como {self.username} desconectou com sucesso!\n')
                    self.active = False
                    self.callback.connections.remove(self)

                elif data_rec.msgType == 'ok  ':
                    ...
                elif data_rec.msgType == 'err ':
                    ...
