import time
from socket import *
from threading import *
import struct
import random

SERVER_PORT = 2040
SERVER_IP = gethostbyname(gethostname())



class Server:
    def __init__(self, ip, port):
        self.udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.ip = ip
        self.port = port
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.start_game = False
        self.All_Teams = {}
        self.Team1 = []
        self.Team2 = []
        

    def send_broadcast_messages(self, message):
        send_until = time.time() + 10
        while time.time() < send_until:
            self.udp_socket.sendto(message, ('<broadcast>', 13117))
            time.sleep(1)
        self.start_game = True

    def game_play(self, client_socket):
        #send Welcome message to client
        welcome_message = "Welcome to Keyboard Spamming Battle Royale.\n"
        welcome_message += "Group 1:\n =="
        for team in self.Team1:
            welcome_message += team + '\n'
        welcome_message += "Group 2:\n =="
        for team in self.Team2:
            welcome_message += team + '\n'
        welcome_message += "Start pressing keys on your keyboard as fast as you can!!"

        client_socket.send(bytes(welcome_message, encoding='utf-8'))
        



    def client_handler(self, client):
        print("Server: Connection Established!")
        team_name = client.recv(1024)
        team_name = team_name.decode('utf-8').strip('\n')
        print(f'Team {team_name} connected!')
        self.All_Teams[team_name] = 0

        # choose team for client - randomly
        group_choice = random.choice([0, 1])
        if group_choice == 0:
            self.Team1.append(team_name)
            group = 'Team 1'
        elif group_choice == 1:
            self.Team2.append(team_name)
            group = 'Team 2'
        print(f'Team: {team_name} added to group {group}')

        while not self.start_game:
            time.sleep(0.2)

        self.game_play(client)

        

        
        #Game - RECV
        #Stastics
        #Send Message
        self.start_game = False

    def TCPServer(self):
        self.tcp_socket.bind((self.ip,self.port))
        print(f'Server started, listening on IP address {SERVER_IP}')
        self.tcp_socket.listen()
        while True:
            client_socket, addr = self.tcp_socket.accept()
            handler_thread = Thread(target=self.client_handler, args=(client_socket,))
            handler_thread.start()



    def start_running(self):
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

    
