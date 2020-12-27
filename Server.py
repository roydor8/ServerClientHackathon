import enum
import time
from socket import *
import threading
import struct

SERVER_PORT = 2040
SERVER_IP = gethostbyname(gethostname())


class ServerState(enum.Enum):
    waiting_for_clients = 1
    game_mode = 2


class Server:
    def __init__(self):
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.state = ServerState.waiting_for_clients

    def waiting_for_clients(self):
        """
        This function sends UDP broadcast messages each 1 sec
        for 10 seconds and listening for clients responses.
        """
        self.udp_socket.bind(('', SERVER_PORT))
        print(f'Server started, listening on IP address {SERVER_IP}')
        message_to_send = struct.pack('bla', 0xfeedbeef, 0x2, 0x7f8)
        send_until = time.time() + 10
        while time.time() < send_until:
            self.udp_socket.sendto(message_to_send, ('<broadcast>', 13117))
            time.sleep(1)
        self.udp_socket.close()

server = Server()
server.waiting_for_clients()
