import time
import traceback
import socket
from threading import *
import struct
# from scapy.all import *
from select import select

SERVER_IP = socket.gethostbyname(socket.gethostname())  # 172.99.0
# SERVER_IP = 'localhost'
# SERVER_IP = get_if_addr("eth1") # 172.1.0
# SERVER_IP = get_if_addr("eth2") # 172.99.0
SERVER_PORT = 13425
UDP_DEST_PORT = 13117
BUFFER_SIZE = 2048
MAGIC_COOKIE = 0xfeedbeef
MSG_TYPE = 0x2


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
        self.team_statistics = {}
        self.Team1 = {}
        self.Team2 = {}
        self.team_threads = {}

    def start_run(self):
        """
        This function will initialize 2 Threads:
        1. sending broadcast UDP message
        2. listen to clients
        """
        self.udp_socket.bind(('', self.port))
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # self.tcp_socket.bind((self.ip, self.port))
        self.tcp_socket.bind(('', self.port))
        self.tcp_socket.listen(1)
        # self.tcp_socket.setblocking(0)
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
        """
        This function will be called as a thread.
        It listens to clients requests to connect and
        connects with them.
        """
        print(f'Server started, listening on IP address {self.ip}')
        while self.is_broadcasting:
            try:
                client_socket, address = self.tcp_socket.accept()
                team_name = client_socket.recv(BUFFER_SIZE).decode().strip('\n')
                print(f'Team {team_name} has connected to server!')
                self.connections[team_name] = (client_socket, address)
            except:
                # traceback.print_exc()
                continue

    def send_broadcast_to_clients(self):
        """
        This function will be called as a thread.
        It send a broadcast messages for 10 seconds every 1 sec.
        """
        broad_message = struct.pack('Ibh', MAGIC_COOKIE, MSG_TYPE, self.port)
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
        """
        This function will close all sockets
        that were used in the program.
        """
        self.close_clients()
        self.tcp_socket.close()
        self.udp_socket.close()

    def close_clients(self):
        """
        This function closes all clients sockets.
        """
        for _, address_tuple in self.connections.items():
            address_tuple[0].close()

    def separate_teams(self):
        """
        This function take all teams name and seperate them into 2 Teams - Team1 and Team2
        each Team is a dictionary : TeamName --> points
        """
        flag = 0
        for team_name, _ in self.connections.items():
            if flag == 0:
                self.Team1[team_name] = 0
                flag = 1
            else:
                self.Team2[team_name] = 0
                flag = 0

    def team_starts_game(self, team_name):
        """
        This function will be called as a thread.
        The server starts the game from his side -
        sends welcome message to all clients connected to the server
        and gets the results from the client's presses
        After all - sends a game over message to clients
        """
        client_socket = self.connections[team_name][0]

        # send a start-game message to client
        msg = "Welcome to '2 Girlz 1 Cup' Keyboard Spamming Battle Royale.\n"
        msg += "Group 1:\n==\n"
        for team in self.Team1:
            msg += f'{team}\n'
        msg += "Group 2:\n==\n"
        for team in self.Team2:
            msg += f'{team}\n'
        msg += "Start pressing keys on your keyboard as fast as you can!!"
        client_socket.send(msg.encode())

        self.team_statistics[team_name] = {}

        count_press = 0
        play_until = time.time() + 10
        while time.time() <= play_until:
            try:
                incoming_char, _, _ = select([client_socket], [], [], 0.2)
                if incoming_char:
                    char_from_client = client_socket.recv(BUFFER_SIZE).decode()
                    if char_from_client in self.team_statistics[team_name]:
                        self.team_statistics[team_name][char_from_client] += 1
                    else:
                        self.team_statistics[team_name][char_from_client] = 1
                    count_press += 1
                    # print(f'{team_name} pressed {char_from_client}')
            except:
                continue

        if team_name in self.Team1:
            self.Team1[team_name] = count_press
        else:
            self.Team2[team_name] = count_press

    def most_common_char(self):
        """This function returns the char with the max value from the dictionary"""
        char_statistics = {}
        for _, dic in self.team_statistics.items():
            for char, counter in dic.items():
                if char in char_statistics:
                    char_statistics[char] += counter
                else:
                    char_statistics[char] = counter

        values_lst = list(char_statistics.values())
        keys_lst = list(char_statistics.keys())
        return keys_lst[values_lst.index(max(values_lst))]

    def game_play(self):
        """
        This function divides all the clients to 2 teams, initiates a thread for each group that
        connected to the server, calculates statistics about the
        characters that was pressed by the clients, and sends
        a 'game-over' message to the clients.
        """

        self.separate_teams()
        # initiate a thread for each team
        for team_name in self.connections.keys():
            team_game_thread = Thread(target=self.team_starts_game, args=(team_name,))
            self.team_threads[team_name] = team_game_thread
            team_game_thread.start()

        for thread in self.team_threads:
            self.team_threads[thread].join()

        # calculate teams score
        points_team1 = 0
        points_team2 = 0
        for team_name in self.Team1:
            points_team1 += self.Team1[team_name]
        for team_name in self.Team2:
            points_team2 += self.Team2[team_name]

        # calculate statistics
        most_common_char = self.most_common_char()

        # send game over message according to the winner
        game_over_msg = "\nGame over!\n"
        game_over_msg += f"Group 1 typed in " + str(points_team1) + " characters. Group 2 typed in " + str(
            points_team2) + " characters."

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

        game_over_msg += f'\nMost commonly typed character: {most_common_char}\n'

        game_over_msg += "\nCongratulations to the winners:\n==\n"
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


def main():
    while True:
        server = Server()
        try:
            server.start_run()
        except:
            server.finish_run()
            continue
        try:
            server.game_play()
            time.sleep(5)
        except:
            server.close_clients()


if __name__ == '__main__':
    main()



