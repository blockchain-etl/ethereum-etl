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

    def _get_bounds_for_points_recursive(self, x, start, end):
        if x < start.x or x > end.x:
            raise OutOfBounds('timestamp {} is out of bounds for blocks {}-{}, timestamps {}-{}'
                              .format(x, start.y, end.y, start.x, end.x))

        if x == start.x:
            return start.y, start.y
        elif x == end.x:
            return end.y, end.y
        elif (end.y - start.y) <= 1:
            return start.y, end.y
        else:
            assert start.x <= x <= end.x
            # Block numbers must increase strictly monotonically
            assert start.x < end.x

            estimation1_y = interpolate(start, end, x)
            estimation1_y = bound_exclusive(estimation1_y, (start.y, end.y))
            estimation1 = self._get_point_for_block(estimation1_y)

            if x > estimation1.x:
                points = (start, estimation1)
            else:
                points = (estimation1, end)

            estimation2_y = interpolate(*points, x)
            estimation2_y = bound_exclusive(estimation2_y, (start.y, end.y))
            estimation2 = self._get_point_for_block(estimation2_y)

            all_points = [start, estimation1, estimation2, end]

            bounds = find_bounds(x, all_points)
            if bounds is None:
                raise ValueError('Unable to find bounds for points {} and x {}'.format(points, x))

            return self._get_bounds_for_points_recursive(x, *bounds)

    def _get_point_for_block(self, block_identifier):
        block = self._web3.eth.getBlock(block_identifier)
        self._request_count = self._request_count + 1
        point = Point(block.timestamp, block.number)
        self.cached_points.append(point)
        return point


def find_bounds(x, points):
    sorted_points = sorted(points, key=lambda point: point.x)
    for point1, point2 in pairwise(sorted_points):
        if point1.x <= x <= point2.x:
            return point1, point2
    return None


def interpolate(point1, point2, x):
    x1, y1 = point1.x, point1.y
    x2, y2 = point2.x, point2.y
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


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '({},{})'.format(self.x, self.y)
