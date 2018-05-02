import sys

socket_path = 'path_to_socket'
buffer_size = 100

if len(sys.argv) > 1:
    socket_path = sys.argv[1]

if len(sys.argv) > 2:
    buffer_size = sys.argv[2]

buffer = ''
current_buffer_size = 0

for line in sys.stdin:
    buffer += line
    current_buffer_size += 1
    if current_buffer_size == buffer_size:
        sys.stdout.write(buffer)
        buffer = ''

if buffer != '':
    sys.stdout.write(buffer)
