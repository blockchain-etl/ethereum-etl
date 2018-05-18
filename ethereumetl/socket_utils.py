import socket

import time

BUFFER_SIZE = 65536  # 64 KiB
ENCODING = 'utf-8'

# Only works on Unix with geth. Sends a new-line delimited JSON RPC request batch, shuts down
# the socket and reads the response until it gets an empty string from the other side.
# Doesn't work in Parity as it interleaves responses with each other. On Windows shutdown is not supported.
class UnixGethIPCWrapper:
    _socket = None

    def __init__(self, ipc_path, timeout=10):
        self.ipc_path = ipc_path
        self.timeout = timeout

    def make_request(self, text):
        return socket_exchange(self.ipc_path, text, self.timeout)


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
            time.sleep(0.1)
        else:
            break
    return data


class SocketTimeoutException(Exception):
    pass
