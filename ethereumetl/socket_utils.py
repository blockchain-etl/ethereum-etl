import socket

import time

BUFFER_SIZE = 65536  # 64 KiB
ENCODING = 'utf-8'


def exchange(socket_path, inp, timeout_seconds=10):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        sock.connect(socket_path)
        sock.sendall(inp.encode(ENCODING))
        sock.shutdown(socket.SHUT_WR)
        response = recv_all(sock, timeout_seconds)
    finally:
        sock.close()
    return response.decode(ENCODING)


def exchange_with_retries(socket_path, inp, max_retries=10, timeout_seconds=5):
    retry_count = 0
    while True:
        try:
            return exchange(socket_path, inp, timeout_seconds)
        except SocketTimeoutException as e:
            retry_count += 1
            if retry_count > max_retries:
                raise e


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
