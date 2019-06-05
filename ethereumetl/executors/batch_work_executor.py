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
import time

from requests.exceptions import Timeout as RequestsTimeout, HTTPError, TooManyRedirects
from web3.utils.threads import Timeout as Web3Timeout

from ethereumetl.executors.bounded_executor import BoundedExecutor
from ethereumetl.executors.fail_safe_executor import FailSafeExecutor
from ethereumetl.misc.retriable_value_error import RetriableValueError
from ethereumetl.progress_logger import ProgressLogger
from ethereumetl.utils import dynamic_batch_iterator

RETRY_EXCEPTIONS = (ConnectionError, HTTPError, RequestsTimeout, TooManyRedirects, Web3Timeout, OSError,
                    RetriableValueError)

BATCH_CHANGE_COOLDOWN_PERIOD_SECONDS = 2 * 60


# Executes the given work in batches, reducing the batch size exponentially in case of errors.
class BatchWorkExecutor:
    def __init__(self, starting_batch_size, max_workers, retry_exceptions=RETRY_EXCEPTIONS, max_retries=5):
        self.batch_size = starting_batch_size
        self.max_batch_size = starting_batch_size
        self.latest_batch_size_change_time = None
        self.max_workers = max_workers
        # Using bounded executor prevents unlimited queue growth
        # and allows monitoring in-progress futures and failing fast in case of errors.
        self.executor = FailSafeExecutor(BoundedExecutor(1, self.max_workers))
        self.retry_exceptions = retry_exceptions
        self.max_retries = max_retries
        self.progress_logger = ProgressLogger()
        self.logger = logging.getLogger('BatchWorkExecutor')

    def execute(self, work_iterable, work_handler, total_items=None):
        self.progress_logger.start(total_items=total_items)
        for batch in dynamic_batch_iterator(work_iterable, lambda: self.batch_size):
            self.executor.submit(self._fail_safe_execute, work_handler, batch)

    def _fail_safe_execute(self, work_handler, batch):
        try:
            work_handler(batch)
            self._try_increase_batch_size(len(batch))
        except self.retry_exceptions:
            self.logger.exception('An exception occurred while executing work_handler.')
            self._try_decrease_batch_size(len(batch))
            self.logger.info('The batch of size {} will be retried one item at a time.'.format(len(batch)))
            for item in batch:
                execute_with_retries(work_handler, [item],
                                     max_retries=self.max_retries, retry_exceptions=self.retry_exceptions)

        self.progress_logger.track(len(batch))

    # Some acceptable race conditions are possible
    def _try_decrease_batch_size(self, current_batch_size):
        batch_size = self.batch_size
        if batch_size == current_batch_size and batch_size > 1:
            new_batch_size = int(current_batch_size / 2)
            self.logger.info('Reducing batch size to {}.'.format(new_batch_size))
            self.batch_size = new_batch_size
            self.latest_batch_size_change_time = time.time()

    def _try_increase_batch_size(self, current_batch_size):
        if current_batch_size * 2 <= self.max_batch_size:
            current_time = time.time()
            latest_batch_size_change_time = self.latest_batch_size_change_time
            seconds_since_last_change = current_time - latest_batch_size_change_time \
                if latest_batch_size_change_time is not None else 0
            if seconds_since_last_change > BATCH_CHANGE_COOLDOWN_PERIOD_SECONDS:
                new_batch_size = current_batch_size * 2
                self.logger.info('Increasing batch size to {}.'.format(new_batch_size))
                self.batch_size = new_batch_size
                self.latest_batch_size_change_time = current_time

    def shutdown(self):
        self.executor.shutdown()
        self.progress_logger.finish()


def execute_with_retries(func, *args, max_retries=5, retry_exceptions=RETRY_EXCEPTIONS, sleep_seconds=1):
    for i in range(max_retries):
        try:
            return func(*args)
        except retry_exceptions:
            logging.exception('An exception occurred while executing execute_with_retries. Retry #{}'.format(i))
            if i < max_retries - 1:
                logging.info('The request will be retried after {} seconds. Retry #{}'.format(sleep_seconds, i))
                time.sleep(sleep_seconds)
                continue
            else:
                raise
