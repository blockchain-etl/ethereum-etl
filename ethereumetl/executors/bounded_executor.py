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