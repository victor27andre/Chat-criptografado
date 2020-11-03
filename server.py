import socket
from handler import ServerHandler


HOST = ''
PORT = 12321

try:
  server_handler = ServerHandler(HOST, PORT)
  server_handler.start()
  server_handler.join()

except KeyboardInterrupt:
  print('')
  print('Encerrando o servidor...')
  server_handler.stop()
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))


print('Hasta la vista baby!')

