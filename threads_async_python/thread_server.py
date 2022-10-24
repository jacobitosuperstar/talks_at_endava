"""
ENDAVA 2022
Threads Async and Python

found at:
github.com/jacobitosuperstar/...
"""

from socket import socket, AF_INET, SOCK_STREAM
from fibonacci import fibonacci

def thread_server(address) -> None:
    """
    Thread server
    """
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.bind(address)
        sock.listen()
        while 1:
            client, address = sock.accept()
            print('\nConnection from: ', address)
            fibonacci_handler(client)


def fibonacci_handler(client: socket) -> None:
    """
    gets the requests and parses it for the fibonacci function
    """
    while 1:
        request = client.recv(10)
        if not request:
            break
        number = int(request)
        response = str(fibonacci(number)) + "\n"
        client.send(response.encode('utf-8'))
    print("Cerrado")


if __name__ == "__main__":
    thread_server(("", 12345))
