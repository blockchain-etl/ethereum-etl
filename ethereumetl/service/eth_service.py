from datetime import datetime, timezone


class EthService(object):
    def __init__(self, web3):
        self._web3 = web3
        self._request_count = 0
        self.cached_points = []

    def get_block_range_for_date(self, date):
        start_datetime = datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
        end_datetime = datetime.combine(date, datetime.max.time(), tzinfo=timezone.utc)
        return self.get_block_range_for_timestamps(start_datetime.timestamp(), end_datetime.timestamp())

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
        bounds = find_bounds(timestamp, self.cached_points)
        if bounds is None:
            bounds = self._get_point_for_block(1), self._get_point_for_block('latest')

        result = self._get_bounds_for_points_recursive(timestamp, *bounds)
        print(self._request_count)
        return result

    def _get_bounds_for_points_recursive(self, y, start, end):
        if y < start.y or y > end.y:
            raise OutOfBounds('timestamp {} is out of bounds for blocks {}-{}, timestamps {}-{}'
                              .format(y, start.x, end.x, start.y, end.y))

        if y == start.y:
            return start.x, start.x
        elif y == end.y:
            return end.x, end.x
        elif (end.x - start.x) <= 1:
            return start.x, end.x
        else:
            assert start.y <= y <= end.y
            # Block numbers must increase strictly monotonically
            assert start.y < end.y

            estimation1_x = interpolate(start, end, y)
            estimation1_x = bound_exclusive(estimation1_x, (start.x, end.x))
            estimation1 = self._get_point_for_block(estimation1_x)

            if y > estimation1.y:
                points = (start, estimation1)
            else:
                points = (estimation1, end)

            estimation2_x = interpolate(*points, y)
            estimation2_x = bound_exclusive(estimation2_x, (start.x, end.x))
            estimation2 = self._get_point_for_block(estimation2_x)

            all_points = [start, estimation1, estimation2, end]

            bounds = find_bounds(y, all_points)
            if bounds is None:
                raise ValueError('Unable to find bounds for points {} and x {}'.format(points, y))

            return self._get_bounds_for_points_recursive(y, *bounds)

    def _get_point_for_block(self, block_identifier):
        block = self._web3.eth.getBlock(block_identifier)
        self._request_count = self._request_count + 1
        point = Point(block.number, block.timestamp)
        self.cached_points.append(point)
        return point


def find_bounds(y, points):
    sorted_points = sorted(points, key=lambda point: point.y)
    for point1, point2 in pairwise(sorted_points):
        if point1.y <= y <= point2.y:
            return point1, point2
    return None


def interpolate(point1, point2, y):
    x1, y1 = point1.x, point1.y
    x2, y2 = point2.x, point2.y
    if x1 == x2:
        raise ValueError('The x coordinate for points is the same')
    x = int((y - y1) * (x2 - x1) / (y2 - y1) + x1)
    return x


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


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({},{})'.format(self.x, self.y)
