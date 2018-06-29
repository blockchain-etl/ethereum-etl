from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore


class BoundedExecutor:
    """BoundedExecutor behaves as a ThreadPoolExecutor which will block on
    calls to submit() once the limit given as "bound" work items are queued for
    execution.
    :param bound: Integer - the maximum number of items in the work queue
    :param max_workers: Integer - the size of the thread pool
    """
    def __init__(self, bound, max_workers):
        self._delegate = ThreadPoolExecutor(max_workers=max_workers)
        self._semaphore = BoundedSemaphore(bound + max_workers)

    """See concurrent.futures.Executor#submit"""
    def submit(self, fn, *args, **kwargs):
        self._semaphore.acquire()
        try:
            future = self._delegate.submit(fn, *args, **kwargs)
        except:
            self._semaphore.release()
            raise
        else:
            future.add_done_callback(lambda x: self._semaphore.release())
            return future

    """See concurrent.futures.Executor#shutdown"""
    def shutdown(self, wait=True):
        self._delegate.shutdown(wait)