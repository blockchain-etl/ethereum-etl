import socket
import sys


def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data

socket_path = 'path_to_socket'
buffer_size = 100

if len(sys.argv) > 1:
    socket_path = sys.argv[1]

if len(sys.argv) > 2:
    buffer_size = sys.argv[2]

buffer = ''
current_buffer_size = 0


def exchange_with_socket(inp):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(socket_path)
    except socket.error as msg:
        print(msg)
        sys.exit(1)

    sock.sendall(inp.encode('utf-8'))
    sock.shutdown(socket.SHUT_WR)
    response = recvall(sock)
    sock.close()
    return response


for line in sys.stdin:
    buffer += line
    current_buffer_size += 1
    if current_buffer_size == buffer_size:
        response = exchange_with_socket(buffer)
        sys.stdout.write(response.decode('utf-8'))
        buffer = ''

if buffer != '':
    sys.stdout.write(exchange_with_socket(buffer).decode('utf-8'))
