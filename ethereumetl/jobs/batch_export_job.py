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


from web3.utils.threads import Timeout

from ethereumetl.executors.bounded_executor import BoundedExecutor
from ethereumetl.executors.fail_safe_executor import FailSafeExecutor
from ethereumetl.jobs.base_job import BaseJob
from ethereumetl.utils import split_to_batches


class BatchExportJob(BaseJob):
    def __init__(
            self,
            range_start,
            range_end,
            batch_size,
            max_workers=5):
        if range_start < 0 or range_end < 0:
            raise ValueError('range_start and range_end must be greater or equal to 0')

        if range_end < range_start:
            raise ValueError('range_end must be greater or equal to range_start')

        if batch_size <= 0:
            raise ValueError('batch_size must be greater than 0')

        if max_workers <= 0:
            raise ValueError('max_workers must be greater than 0')

        self.start = range_start
        self.end = range_end
        self.batch_size = batch_size
        self.max_workers = max_workers

        self.executor = None

    def _start(self):
        # Using bounded executor prevents unlimited queue growth
        # and allows monitoring in-progress futures and failing fast in case of errors.
        self.executor = FailSafeExecutor(BoundedExecutor(1, self.max_workers))

    def _export(self):
        for batch_start, batch_end in split_to_batches(self.start, self.end, self.batch_size):
            self.executor.submit(self._fail_safe_export_batch, batch_start, batch_end)

    def _fail_safe_export_batch(self, batch_start, batch_end):
        try:
            self._export_batch(batch_start, batch_end)
        except (Timeout, OSError):
            # try exporting one by one
            for block_number in range(batch_start, batch_end + 1):
                self._export_batch(block_number, block_number)

    def _export_batch(self, batch_start, batch_end):
        pass

    def _end(self):
        self.executor.shutdown()
