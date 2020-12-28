from Server import Server
from Client import Client


def main():
    server = Server('localhost', 2040)
    server.start_running()

    client_Roy = Client()
    client_Roy.start_running()


if __name__ == '__main__':
    main()
