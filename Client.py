from struct import *
from socket import *
import enum
from threading import *
import os

HOST = gethostname()
localPORT = 13117
buffer_size = 2048



class Client:
    def __init__(self):
        self.team_name = "Mr. & Ms. Dor"
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.game_is_on = False

    def listen_to_server(self):
        self.tcp_socket.listen()
        while True:
            message = self.tcp_socket.recv()
            if message:
                print(str(message, 'utf8'))
        

    def send_keypress_to_server(self):
        # send key press to server
        while True:
            os.system("stty -raw echo")
            key = sys.stdin.read(1)



    def game_play(self):
        # listen_to_server_thread = Thread(target=self.listen_to_server)
        # send_keypress_thread = Thread(target=send_keypress_to_server)
        # listen_to_server_thread.start()
        # send_keypress_thread.start()

        while True:
            try:
                message = self.tcp_socket.recv(2048)
            except:
                pass
            if not message:
                os.system("stty raw -echo")
                key = sys.stdin.read(1)
                this.tcp_socket.send(bytes(key, encoding='utf-8'))
            else:
                os.system("stty -raw echo")
                message = str(message, 'utf-8')
                print(message)
                break




    def connect_to_server(self, server_address, port_from_message):
        self.tcp_socket.connect(('localhost',2040))
        self.tcp_socket.setblocking(False)
        message_to_send = self.team_name + '\n'
        self.tcp_socket.send(bytes(message_to_send, encoding='utf-8'))
        # move to game mode
        self.game_play()
        

    def start_running(self):
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




