from struct import *
from socket import *
import enum

HOST = gethostname()
localPORT = 13117
buffer_size = 2048



class Client:
    def __init__(self):
        self.team_name = "Mr. & Ms. Dor"
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)

    def connect_to_server(self, server_address, port_from_message):
        self.tcp_socket.connect(('localhost',2040))

        message_to_send = self.team_name + '\n'
        self.tcp_socket.send(bytes(message_to_send, encoding='utf-8'))

    def look_for_server(self):
        try:
            self.udp_socket.bind(('',13117))
        except:
            pass
        print("Client started, listening for offer requests...")

        message, server_address = self.udp_socket.recvfrom(buffer_size)

        print(f'Received offer from {server_address}, attempting to connect...')
        #TODO: RECEIVE PORT FROM MSG
        msg_port = ''

        print(f'DEBUG: Server message: {message}')
        print(f'DEBUG: Server IP: {server_address}')

        self.connect_to_server(server_address, msg_port)




