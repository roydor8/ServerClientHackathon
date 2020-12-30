import time
import traceback
import socket
from threading import *
import struct
import random
from scapy.all import *


SERVER_IP = socket.gethostbyname(socket.gethostname())
# SERVER_IP = get_if_addr("eth1")
SERVER_PORT = 12345
UDP_DEST_PORT = 13117
BUFFER_SIZE = 2048


class Server:
    def __init__(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = SERVER_IP
        self.port = SERVER_PORT
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start_game = False
        self.is_broadcasting = False
        self.next_team_to_append = 0
        self.connections = {}
        self.All_Teams = {}
        self.Team1 = {}
        self.Team2 = {}
        self.team_threads = {}

    def start_run(self):
        self.udp_socket.bind(('', self.port))
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.tcp_socket.bind(('', self.port))
        self.tcp_socket.listen()
        self.tcp_socket.settimeout(3)
        broadcast_thread = Thread(target=self.send_broadcast_to_clients)
        listen_to_clients_thread = Thread(target=self.listen_to_clients)
        broadcast_thread.start()
        listen_to_clients_thread.start()
        listen_to_clients_thread.join()
        broadcast_thread.join()
        self.udp_socket.close()
        self.tcp_socket.close()

    def listen_to_clients(self):
        print(f'Server started, listening on IP address {SERVER_IP}')
        while self.is_broadcasting:
            try:
                client_socket, address = self.tcp_socket.accept()
                team_name = client_socket.recv(BUFFER_SIZE).decode().strip('\n')
                print(f'Server: Team {team_name} has connected to server!')
                self.connections[team_name] = (client_socket, address)
            except:
                traceback.print_exc()
                continue

    def send_broadcast_to_clients(self):
        broad_message = struct.pack('Ibh', 0xfeedbeee, 0x2, self.port)
        send_until = time.time() + 10
        self.is_broadcasting = True
        # counter = 1
        while time.time() < send_until:
            address = ('<broadcast>', UDP_DEST_PORT)
            self.udp_socket.sendto(broad_message, address)
            # print(f'Broadcast message number {counter} sent')
            time.sleep(1)
            # counter += 1
        self.is_broadcasting = False

    def finish_run(self):
        # self.client_sockets_close()
        self.tcp_socket.close()
        self.udp_socket.close()

    def close_clients(self):
        for _, add_tup in self.connections.items():
            add_tup[0].close()

    def separate_teams(self):
        flag = 0
        for team_name, _ in self.connections.items():
            if flag == 0:
                self.Team1[team_name] = 0
                flag = 1
            else:
                self.Team2[team_name] = 0
                flag = 0

    def team_starts_game(self, team_name):
        client_socket = self.connections[team_name][0]
        # send a start-game message to client
        msg = "Welcome to Keyboard Spamming Battle Royale.\n"
        msg += "Group 1:\n==\n"
        for team in self.Team1:
            msg += f'{team}\n'
        msg += "Group 2:\n==\n"
        for team in self.Team2:
            msg += f'{team}\n'
        msg += "Start pressing keys on your keyboard as fast as you can!!"
        client_socket.send(msg.encode())

        count_press = 0
        play_until = time.time() + 10
        while time.time() <= play_until:
            try:
                char_from_client = client_socket.recv(2048).decode()
            except:
                continue
            print(char_from_client)
            count_press += 1
        print("Time finished")
        if team_name in self.Team1:
            self.Team1[team_name] = count_press
        if team_name in self.Team2:
            self.Team2[team_name] = count_press
        else:
            print("ERROR- this team is not a part of the game")

    def game_play(self):
        self.separate_teams()
        self.Team2['Daba'] = 4
        for team_name in self.connections.keys():
            team_game_thread = Thread(target=self.team_starts_game, args=(team_name,))
            self.team_threads[team_name] = team_game_thread
            team_game_thread.start()

        for thread in self.team_threads:
            self.team_threads[thread].join()
        # print("Threads finished")
        points_team1 = 0
        points_team2 = 0
        for team_name in self.Team1:
            points_team1 += self.Team1[team_name]
        for team_name in self.Team2:
            points_team2 += self.Team2[team_name]

        game_over_msg = "Game over!\n"
        game_over_msg += f"Group 1 typed in " + str(points_team1) + " characters. Group 2 typed in " + str(points_team2) + " characters."

        winner = 0
        if points_team1 > points_team2:
            winner = 1
            game_over_msg += "\nGroup 1 wins!"
        elif points_team2 > points_team1:
            game_over_msg += "\n Group 2 wins!"
            winner = 2
        else:
            game_over_msg += "\nIt's a draw!"
        game_over_msg += "\n"
        game_over_msg += "\nCongratulations to the winners:\n=="
        if winner == 1:
            for team_name in self.Team1:
                game_over_msg += team_name + "\n"
        if winner == 2:
            for team_name in self.Team2:
                game_over_msg += team_name + "\n"

        game_over_msg += "\nGame Over, sending out offer requests..."
        for team_name in self.connections.keys():
            self.connections[team_name][0].send(game_over_msg.encode())
            print(f'Game over sent to {team_name}')
            self.connections[team_name][0].close()


while True:
    server = Server()
    try:
        server.start_run()
    except:
        server.finish_run()
        continue
    try:
        server.game_play()
    except:
        server.close_clients()
