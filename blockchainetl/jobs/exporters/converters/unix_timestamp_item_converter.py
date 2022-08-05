# MIT License
#
# Copyright (c) 2020 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime
from enum import Enum

from blockchainetl.jobs.exporters.converters.simple_item_converter import SimpleItemConverter


def to_timestamp(value):
    if isinstance(value, int):
        return datetime.utcfromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
    else:
        return value


def to_datetime(value):
    if isinstance(value, int):
        return datetime.utcfromtimestamp(value)
    else:
        return value


class TimestampConversionFunctions(Enum):
    DATETIME = to_datetime
    TIMESTAMP_STRING = to_timestamp


class UnixTimestampItemConverter(SimpleItemConverter):
    def __init__(self,
                 conversion_function: TimestampConversionFunctions = TimestampConversionFunctions.TIMESTAMP_STRING):
        self.conversion_function = conversion_function

    def convert_field(self, key, value):
        if key is not None and key.endswith('timestamp'):
            return self.conversion_function(value)
        else:
            return value
