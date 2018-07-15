from datetime import datetime, timezone

from ethereumetl.service.graph_operations import GraphOperations, OutOfBoundsError, Point


class EthService(object):
    def __init__(self, web3):
        graph = BlockTimestampGraph(web3)
        self._graph_operations = GraphOperations(graph)

    def get_block_range_for_date(self, date):
        start_datetime = datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
        end_datetime = datetime.combine(date, datetime.max.time(), tzinfo=timezone.utc)
        return self.get_block_range_for_timestamps(start_datetime.timestamp(), end_datetime.timestamp())

    def get_block_range_for_timestamps(self, start_timestamp, end_timestamp):
        start_timestamp = int(start_timestamp)
        end_timestamp = int(end_timestamp)
        if start_timestamp > end_timestamp:
            raise ValueError('start_timestamp must be greater or equal to end_timestamp')

        try:
            start_block_bounds = self._graph_operations.get_bounds_for_y_coordinate(start_timestamp)
        except OutOfBoundsError:
            start_block_bounds = (0, 0)

        end_block_bounds = self._graph_operations.get_bounds_for_y_coordinate(end_timestamp)

        if start_block_bounds == end_block_bounds and start_block_bounds[0] != start_block_bounds[1]:
            raise ValueError('The given timestamp range does not cover any blocks')

        start_block = start_block_bounds[1]
        end_block = end_block_bounds[0]

        # The genesis block has timestamp 0 but we include it with the 1st block.
        if start_block == 1:
            start_block = 0

        return start_block, end_block


class BlockTimestampGraph(object):
    def __init__(self, web3):
        self._web3 = web3

    def get_first_point(self):
        # Ignore the genesis block as its timestamp is 0
        return block_to_point(self._web3.eth.getBlock(1))

    def get_last_point(self):
        return block_to_point(self._web3.eth.getBlock('latest'))

    def get_point(self, x):
        return block_to_point(self._web3.eth.getBlock(x))


def block_to_point(block):
    return Point(block.number, block.timestamp)
