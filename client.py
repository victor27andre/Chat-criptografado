import socket
import threading
import time
import protocol as cp

HOST = 'localhost'
PORT = 12321


def handle_received_message(sock):
    while True:
        try:
            data = sock.recv(1024)
        except ConnectionAbortedError:
            exit()
        data = cp.read_incoming(data)
        if data.msgType == 'brod':
            print(f'Broadcast recebido: ({data.msgValue.split(" ")[0]}) {" ".join(data.msgValue.split(" ")[1:])}')
        elif data.msgType == 'priv':
            print(f'Mensagem privada recebida recebido: {data.msgValue}')
        elif data.msgType == 'ok  ':
            print(f'Comando realizado com sucesso:\n {data.msgValue}')
        elif data.msgType == 'err ':
            print('Erro:\n' + error_dict[data.msgValue])
        elif data.msgType == 'clos':
            print('Servidor fechando, finalizando processo')
            sock.close()
            exit()
        # print('')
        # print(f'Received {data.decode("utf-8")}')




with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    error_dict = {'001': '',
                  '002': '',
                  '003': '',
                  '004': '',
                  '005': '',
                  '006': '',
                  '007': '',
                  '008': '',
                  '009': '',
                  }
    s.connect((HOST, PORT))

    while True:
        username = input('Digite seu nome de usuário: ')
        user_msg = cp.prepare_to_send('user', username)
        s.sendall(user_msg.encode())

        data = s.recv(1024)
        user_resp = cp.read_incoming(data)

        if user_resp.msgType == 'ok  ':
            print('Usuario aceito,prossiga com a senha...')
            break
        elif user_resp.msgType == 'err ':
            print('Erro:\n' + error_dict[user_resp.msgValue])

    while True:
        username = input('Digite sua senha: ')
        user_msg = cp.prepare_to_send('pass', username)
        s.sendall(user_msg.encode())

        data = s.recv(1024)
        user_resp = cp.read_incoming(data)

        if user_resp.msgType == 'ok  ':
            print('Senha aceita,conectado com sucesso...')
            break
        elif user_resp.msgType == 'err ':
            print('Erro:\n' + error_dict[user_resp.msgValue])

    # class activation:
    #     def __init__(self):
    #         self.active = True
    #
    # active_flag = activation()

    t = threading.Thread(target=handle_received_message, args=(s,))
    t.start()

    while True:
        try:
            time.sleep(.1)
            comando = 'mesg'
            text = input('Digite uma mensagem a ser enviada ao servidor: \n')
            if text[0] == '-':
                comando = text[1:5]
                text = text[6:]
                if comando == 'priv':
                    pass
                elif comando == 'mesg':
                    pass
                elif comando == 'retr' or comando == 'clos':
                    text = ''
                else:
                    print('Comando inválido.')
                    continue

            msg = cp.prepare_to_send(comando, text)
            s.sendall(msg.encode())
            if comando == 'clos':
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            print('')
            print('Encerrando o cliente...')
            s.close()
            break

print('Bye bye!')
