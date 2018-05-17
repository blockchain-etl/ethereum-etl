import socket
import sys

import time

BUFFER_SIZE = 65536  # 64 KiB
ENCODING = 'utf-8'


def socket_exchange(socket_path, request, timeout_seconds=10):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        sock.connect(socket_path)
        sock.sendall(request.encode(ENCODING))
        sock.shutdown(socket.SHUT_WR)
        response = recv_all(sock, timeout_seconds)
    finally:
        sock.close()
    return response.decode(ENCODING)


def socket_exchange_geth_unix(socket_path, request, timeout_seconds=10):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        sock.connect(socket_path)
        sock.sendall(request.encode(ENCODING))
        sock.shutdown(socket.SHUT_WR)
        response = recv_all(sock, timeout_seconds)
    finally:
        sock.close()
    return response.decode(ENCODING)



def get_ipc_socket(ipc_path):
    if sys.platform == 'win32':
        # On Windows named pipe is used. Simulate socket with it.
        from web3.utils.windows import NamedPipe

        return NamedPipe(ipc_path)
    else:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(ipc_path)
        return sock


# https://www.binarytides.com/receive-full-data-with-the-recv-socket-function-in-python/
def recv_all(sock, timeout=10):
    data = b''
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            raise SocketTimeoutException('Timeout while receiving data from socket')

        part = sock.recv(BUFFER_SIZE)

        if len(part) != 0:
            data += part
            start_time = time.time()
        elif len(data) == 0:
            # sleep for some time to indicate a gap
            time.sleep(0.05)
        else:
            break
    return data


class SocketTimeoutException(Exception):
    pass
