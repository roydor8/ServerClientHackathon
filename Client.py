import struct
import traceback
from struct import *
from socket import *
import enum
from threading import *
import os
import sys
import keyboard
from select import select

CLIENT_IP = '127.0.0.1' 
# CLIENT_IP = gethostbyname(gethostname())
localPORTUDP = 13117
localPORTTCP = 12346  # todo switch back to 2040
BUFFER_SIZE = 1024


class Client:
    def __init__(self):
        self.team_name = "Mr. & Ms. Dor"
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.game_is_on = False

    def start_run(self):
        print("Client Started, listening for offer request...")
        self.udp_socket.bind(('', localPORTUDP))
        while True:
            try:
                msg, server_address = self.udp_socket.recvfrom(BUFFER_SIZE)
                unpacked_msg = struct.unpack('Ibh', msg)
                magic_cookie = unpacked_msg[0]
                msg_type = unpacked_msg[1]
                server_port = unpacked_msg[2]
                server_ip = server_address[0]
                if magic_cookie != 0xfeedbeea or msg_type != 0x2:
                    continue
                print(f'Received offer from {server_ip}, attempting to connect...')
                self.connect_to_server(server_ip, server_port)
                try:
                    # send team name to server
                    team_name_message = self.team_name + '\n'
                    self.tcp_socket.send(team_name_message.encode())
                except:
                    self.tcp_socket.close()
                    continue
                break
            except:
                continue
        self.udp_socket.close()

    def connect_to_server(self, server_ip, server_port):
        # self.tcp_socket.bind((server_ip, localPORTTCP))
        self.tcp_socket.bind(('localhost', localPORTTCP))
        # self.tcp_socket.connect(('localhost', server_port))
        self.tcp_socket.connect((server_ip, server_port))
        print("Connected to Server")

    def send_to_server(self, event):
        try:
            self.tcp_socket.send(event.name.encode())
        except:
            print("something went wrong - with key pressing sending from CLIENT to SERVER")

    def keyboard_presser(self):
        # print("trying pressing")
        counter_press = 0
        keyboard.on_press(self.send_to_server)
        while self.game_is_on:
            continue
        print("stopped typing")

    def finish_run(self):
        self.tcp_socket.close()

    # def game_play(self):
    #     try:
    #         keyboard_thread = Thread(target=self.keyboard_presser)
    #         msg = self.tcp_socket.recv(2048).decode()
    #         print(msg)  # game started
    #         self.game_is_on = True
    #         keyboard_thread.start()
    #         msg = self.tcp_socket.recv(2048).decode()
    #         self.game_is_on = False
    #         keyboard_thread.join()
    #         print(msg)  # game ended
    #         print("Server disconnected, listening for offer requests...")
    #         self.tcp_socket.close()
    #         return
    #     except:
    #         # traceback.print_exc()
    #         self.finish_run()
    #         return

    

    def game_play(self):
        message = self.tcp_socket.recv(2048)
        message = str(message, 'utf-8')
        print(message)
        message = None
        while True:
            try:
                incoming_message, _, _ = select([self.tcp_socket],[],[],0.2)
                if incoming_message:
                    message = self.tcp_socket.recv(2048)
            except:
                pass
            if not message:
                os.system("stty raw -echo")
                char_coming, _, _ = select([sys.stdin],[],[],0.2)
                if char_coming:
                    key = sys.stdin.read(1)
                    self.tcp_socket.send(key.encode())
            else:
                os.system("stty -raw echo")
                message = str(message, 'utf-8')
                print(message)
                break
        self.udp_socket.close()


while True:
    client = Client()
    client.start_run()
    try:
        client.game_play()
    except:
        # traceback.print_exc()
        continue
