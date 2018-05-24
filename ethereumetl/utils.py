def hex_to_dec(hex_string):
    if hex_string is None:
        return None
    try:
        return int(hex_string, 16)
    except ValueError:
        print("Not a hex string %s" % hex_string)
        return hex_string


def chunk_string(string, length):
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def batch_readlines(file, batch_size):
    current_batch_size = 0
    batch = []
    for line in file:
        batch.append(line)
        current_batch_size += 1
        if current_batch_size == batch_size:
            yield batch
            batch = []
            current_batch_size = 0
    if current_batch_size != 0:
        yield batch


def to_normalized_address(address):
    if address is None or not isinstance(address, str):
        return address
    return address.lower()


def batch_iterator(iterator, batch_size):
    current_batch = []
    for item in iterator:
        current_batch.append(item)
        if len(current_batch) == batch_size:
            yield current_batch
            current_batch = []

    if len(current_batch) != 0:
        yield current_batch


def split_to_batches(start_incl, end_incl, batch_size):
    """start_incl and end_incl are inclusive, the returned batch ranges are also inclusive"""
    for batch_start in range(start_incl, end_incl + 1, batch_size):
        batch_end = min(batch_start + batch_size - 1, end_incl)
        yield batch_start, batch_end
