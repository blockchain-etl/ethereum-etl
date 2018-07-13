class EthService(object):
    def __init__(self, web3):
        self._web3 = web3
        self._request_count = 0

    def get_block_range_for_timestamps(self, timestamp_start, timestamp_end):
        start_blocks = self.get_block_number_bounds_for_timestamp(timestamp_start)
        end_blocks = self.get_block_number_bounds_for_timestamp(timestamp_end)

        return start_blocks[1], end_blocks[0]

    def get_block_number_bounds_for_timestamp(self, timestamp):
        start_block = self._web3.eth.getBlock(1)
        end_block = self._web3.eth.getBlock('latest')
        self._request_count = self._request_count + 2

        result = self._get_block_number_bounds_for_timestamp_recursive(timestamp, start_block, end_block)
        print('request count', self._request_count)
        return result

    def _get_block_number_bounds_for_timestamp_recursive(self, timestamp, start_block, end_block):
        start_number, end_number = start_block.number, end_block.number
        start_timestamp, end_timestamp = start_block.timestamp, end_block.timestamp

        if timestamp < start_timestamp or timestamp > end_timestamp:
            raise ValueError('timestamp {} is out of bounds for blocks {}-{}, timestamps {}-{}'
                             .format(timestamp, start_number, end_number, start_timestamp, end_timestamp))

        if timestamp == start_timestamp:
            return start_timestamp, start_timestamp
        elif timestamp == end_timestamp:
            return end_number, end_number
        elif (end_number - start_number) <= 1:
            print(start_number, end_number)
            return start_number, end_number
        else:
            assert start_timestamp <= timestamp <= end_timestamp
            # Block numbers must increase strictly monotonically
            assert start_timestamp < end_timestamp
            timestamp_difference = end_timestamp - start_timestamp
            timestamp_increment = timestamp - start_timestamp
            number_difference = end_number - start_number
            estimated_number_increment = int(timestamp_increment * number_difference / timestamp_difference)

            estimated_number = start_number + estimated_number_increment
            estimated_block = self._web3.eth.getBlock(estimated_number)
            self._request_count = self._request_count + 1
            estimated_timestamp = estimated_block.timestamp

            middle_number = start_number + int((end_number - start_number) / 2)
            middle_block = self._web3.eth.getBlock(middle_number)
            self._request_count = self._request_count + 1
            middle_timestamp = middle_block.timestamp

            all_points = [(start_timestamp, start_block), (middle_timestamp, middle_block),
                          (estimated_timestamp, estimated_block), (end_timestamp, end_block)]

            sorted_points = sorted(all_points, key=lambda x: x[0])

            for pair in pairwise(sorted_points):
                if pair[0][0] <= timestamp <= pair[1][0]:
                    new_block_range = pair[0][1], pair[1][1]
                    break
            else:
                raise ValueError('Something is wrong')

            return self._get_block_number_bounds_for_timestamp_recursive(timestamp, new_block_range[0],
                                                                         new_block_range[1])


import itertools
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)