from web3.utils.threads import Timeout

from ethereumetl.executors.bounded_executor import BoundedExecutor
from ethereumetl.executors.fail_safe_executor import FailSafeExecutor
from ethereumetl.jobs.base_job import BaseJob
from ethereumetl.utils import split_to_batches


class BatchExportJob(BaseJob):
    def __init__(
            self,
            start,
            end,
            batch_size,
            max_workers=5):
        self.start = start
        self.end = end
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
