class EthService(object):
    def __init__(self, web3):
        self._web3 = web3
        self._request_count = 0

    def get_block_range_for_timestamps(self, start_timestamp, end_timestamp):
        if start_timestamp > end_timestamp:
            raise ValueError('start_timestamp must be greater or equal to end_timestamp')

        try:
            start_block_bounds = self.get_block_number_bounds_for_timestamp(start_timestamp)
        except OutOfBounds:
            start_block_bounds = (0, 0)

        end_block_bounds = self.get_block_number_bounds_for_timestamp(end_timestamp)

        if start_block_bounds == end_block_bounds and start_block_bounds[0] != start_block_bounds[1]:
            raise ValueError('The given timestamp range does not cover any blocks')

        start_block = start_block_bounds[1]
        end_block = end_block_bounds[0]

        if start_block == 1:
            start_block = 0

        return start_block, end_block

    def get_block_number_bounds_for_timestamp(self, timestamp):
        start_block = self._web3.eth.getBlock(1)
        end_block = self._web3.eth.getBlock('latest')
        self._request_count = self._request_count + 2

        result = self._get_block_number_bounds_for_timestamp_recursive(timestamp, start_block, end_block)
        print(self._request_count)
        return result

    def _get_block_number_bounds_for_timestamp_recursive(self, timestamp, start_block, end_block):
        start_number, end_number = start_block.number, end_block.number
        start_timestamp, end_timestamp = start_block.timestamp, end_block.timestamp

        if timestamp < start_timestamp or timestamp > end_timestamp:
            raise OutOfBounds('timestamp {} is out of bounds for blocks {}-{}, timestamps {}-{}'
                              .format(timestamp, start_number, end_number, start_timestamp, end_timestamp))

        if timestamp == start_timestamp:
            return start_number, start_number
        elif timestamp == end_timestamp:
            return end_number, end_number
        elif (end_number - start_number) <= 1:
            return start_number, end_number
        else:
            assert start_timestamp <= timestamp <= end_timestamp
            # Block numbers must increase strictly monotonically
            assert start_timestamp < end_timestamp

            estimation1_number = interpolate((start_timestamp, start_number), (end_timestamp, end_number), timestamp)
            estimation1_number = bound_exclusive(estimation1_number, (start_number, end_number))
            estimation1_block = self._web3.eth.getBlock(estimation1_number)
            self._request_count = self._request_count + 1
            estimation1_timestamp = estimation1_block.timestamp

            if timestamp > estimation1_timestamp:
                points = ((start_timestamp, start_number), (estimation1_timestamp, estimation1_number))
            else:
                points = ((estimation1_timestamp, estimation1_number), (end_timestamp, end_number))

            estimation2_number = interpolate(*points, timestamp)
            estimation2_number = bound_exclusive(estimation2_number, (start_number, end_number))
            estimation2_block = self._web3.eth.getBlock(estimation2_number)
            self._request_count = self._request_count + 1
            estimation2_timestamp = estimation2_block.timestamp

            all_points = [(start_timestamp, start_block), (estimation1_timestamp, estimation1_block),
                          (estimation2_timestamp, estimation2_block), (end_timestamp, end_block)]

            sorted_points = sorted(all_points, key=lambda x: x[0])

            for (first_timestamp, first_block), (second_timestamp, second_block) in pairwise(sorted_points):
                if first_timestamp <= timestamp <= second_timestamp:
                    new_block_range = first_block, second_block
                    break
            else:
                raise ValueError('Something is wrong')

            return self._get_block_number_bounds_for_timestamp_recursive(timestamp, *new_block_range)


def interpolate(point1, point2, x):
    x1, y1 = point1
    x2, y2 = point2
    if x1 == x2:
        raise ValueError('The x coordinate for points is the same')
    y = int((x - x1) * (y2 - y1) / (x2 - x1) + y1)
    return y


def bound_exclusive(x, bounds):
    x1, x2 = bounds
    if x1 > x2:
        x, x2 = x2, x1
    if x <= x1:
        return x1 + 1
    elif x >= x2:
        return x2 - 1
    else:
        return x


import itertools


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


class OutOfBounds(Exception):
    pass
