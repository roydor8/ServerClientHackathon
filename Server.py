import enum
import time
from socket import *
from threading import *
import struct
import random

SERVER_PORT = 2040
SERVER_IP = gethostbyname(gethostname())



class Server:
    def __init__(self,ip,port):
        self.udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.ip = ip
        self.port = port
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.connections = {}
        self.start = False
        self.All_Teams = {}
        self.TeamA = []
        self.TeamB = []
        

    def send_broadcast_messages(self, message):
        send_until = time.time() + 10
        while time.time() < send_until:
            self.udp_socket.sendto(message, ('<broadcast>', 13117))
            time.sleep(1)
        #RANDOM
        self.start = True

    def client_handler(self, client):
        print("Server: Connection Established!")
        team_name = client.recv(1024)
        team_name = team_name.decode('utf-8')
        print(f'Team {team_name} connected!')
        self.All_Teams[team_name] = 0
        
        # choose team for client - randomly
        
        while not self.start:
            time.sleep(0.2)

        
        r
        #SEND MESSAGE
        #Game - RECV
        #Stastics
        #Send Message

        self.start = False

    def TCPServer(self):
        self.tcp_socket.bind((self.ip,self.port))
        print(f'Server started, listening on IP address {SERVER_IP}')
        self.tcp_socket.listen()
        while True:
            client_socket, addr = self.tcp_socket.accept()
            handler_thread = Thread(target=self.client_handler, args=(client_socket,))
            handler_thread.start()



    def waiting_for_clients(self):
        """
            This function sends UDP broadcast messages each 1 sec
            for 10 seconds and listening for clients responses.
        """
    
        self.udp_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.udp_socket.settimeout(0.2)
        message_to_send = struct.pack('Ibh', 0xfeedbeef, 0x2, 0x7f8)
        
        server_thread = Thread(target=self.TCPServer)
        server_thread.start()
        
        broadcast_thread = Thread(target=self.send_broadcast_messages,args=(message_to_send,))
        broadcast_thread.start()

    def game_play(self, client_socket, address):
        self.state = ServerState.game_mode

