from web3.utils.threads import Timeout

from ethereumetl.executors.bounded_executor import BoundedExecutor
from ethereumetl.executors.fail_safe_executor import FailSafeExecutor
from ethereumetl.utils import dynamic_batch_iterator


class BatchWorkExecutor:
    def __init__(
            self,
            starting_batch_size,
            max_workers):
        self.batch_size = starting_batch_size
        self.max_workers = max_workers
        self.executor = None

    def start(self):
        self.executor = FailSafeExecutor(BoundedExecutor(1, self.max_workers))

    def execute(self, work_iterator, work_handler):
        for batch in dynamic_batch_iterator(work_iterator, lambda: self.batch_size):
            self.executor.submit(self._fail_safe_execute, work_handler, batch)

    # Check race conditions
    def _fail_safe_execute(self, work_handler, batch):
        try:
            work_handler(batch)
        except (Timeout, OSError) as err:
            batch_size = self.batch_size
            # If can't reduce the batch size further then raise
            if batch_size == 1:
                raise err
            # Reduce the batch size, next batch will be 2 times smaller
            if batch_size == len(batch):
                self.batch_size = max(1, int(batch_size / 2))
            # For the failed batch try handling one by one
            for item in batch:
                work_handler([item])

    def end(self):
        self.executor.shutdown()
