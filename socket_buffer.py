import socket
import sys

import time

from ethereumetl.utils import smart_open

socket_path = 'path_to_socket'
buffer_size = 100

def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) == 0:
            # either 0 or end of data
            break
    return data


def recv_timeout(the_socket, expected_count=100, timeout=5):
    # make socket non blocking
    the_socket.setblocking(0)

    # total data partwise in an array
    total_data = b''
    total_count = 0

    # beginning time
    begin = time.time()
    while 1:
        # if you got some data, then break after timeout
        if total_data and time.time() - begin > timeout:
            break

        # if you got no data at all, wait a little longer, twice the timeout
        elif time.time() - begin > timeout * 2:
            break

        # recv something
        try:
            data = the_socket.recv(1000000)
            if data:
                total_data += data
                total_count += 1
                # if total_count == expected_count:
                #     break
                # change the beginning time for measurement
                begin = time.time()
            else:
                # sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass

    # join all parts to make final string
    return total_data


if len(sys.argv) > 1:
    socket_path = sys.argv[1]

if len(sys.argv) > 2:
    buffer_size = sys.argv[2]


def exchange_with_socket(inp):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(socket_path)
    except socket.error as msg:
        print(msg)
        sys.exit(1)

    sock.settimeout(20)
    # inp += '1\n'
    sock.sendall(inp.encode('utf-8'))
    sock.shutdown(socket.SHUT_WR)
    response = recvall(sock)
    sock.close()
    return response.decode('utf-8')


def readlines_batch(file, batch_size):
    current_batch_size = 0
    batch = ''
    for line in file.readlines():
        batch += line
        current_batch_size += 1
        if current_batch_size == batch_size:
            yield batch
            batch = ''
            current_batch_size = 0
    if current_batch_size != 0:
        yield batch


with smart_open('blocks_rpc.json', 'r') as input_file:
    for lines_batch in readlines_batch(input_file, buffer_size):
        response = exchange_with_socket(lines_batch)
        sys.stdout.write(response)

