from Server import Server
from Client import Client


def main():
    server = Server('localhost', 2040)
    client = Client()
    server.waiting_for_clients()
    client.look_for_server()


if __name__ == '__main__':
    main()
