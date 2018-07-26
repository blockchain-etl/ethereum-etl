# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
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

import logging
from datetime import datetime

from ethereumetl.atomic_counter import AtomicCounter


# Thread safe progress logger.
class ProgressLogger:
    def __init__(self, name='work', logger=None, log_percentage_step=10, log_item_step=5000):
        self.name = name
        self.total_items = None

        self.start_time = None
        self.end_time = None
        self.counter = AtomicCounter()
        self.log_percentage_step = log_percentage_step
        self.log_items_step = log_item_step
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger('ProgressLogger')

    def start(self, total_items=None):
        self.total_items = total_items
        self.start_time = datetime.now()
        start_message = 'Started {}.'.format(self.name)
        if self.total_items is not None:
            start_message = start_message + ' Items to process: {}.'.format(self.total_items)
        self.logger.info(start_message)

    # A race condition is possible where a message for the same percentage is printed twice, but it's a minor issue
    def track(self, item_count=1):
        processed_items = self.counter.increment(item_count)
        processed_items_before = processed_items - item_count

        track_message = None
        if self.total_items is None:
            if int(processed_items_before / self.log_items_step) != int(processed_items / self.log_items_step):
                track_message = '{} items processed.'.format(processed_items)
        else:
            percentage = processed_items * 100 / self.total_items
            percentage_before = processed_items_before * 100 / self.total_items
            if int(percentage_before / self.log_percentage_step) != int(percentage / self.log_percentage_step):
                track_message = '{} items processed. Progress is {}%'.format(processed_items, int(percentage)) + \
                                ('!!!' if int(percentage) > 100 else '.')

        if track_message is not None:
            self.logger.info(track_message)

    def finish(self):
        duration = None
        if self.start_time is not None:
            self.end_time = datetime.now()
            duration = self.end_time - self.start_time

        finish_message = 'Finished {}. Total items processed: {}.'.format(self.name, self.counter.increment() - 1)
        if duration is not None:
            finish_message = finish_message + ' Took {}.'.format(str(duration))

        self.logger.info(finish_message)
