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


class FailSafeExecutor:

    def __init__(self, delegate):
        self._delegate = delegate
        self._futures = []

    def submit(self, fn, *args, **kwargs):
        self._check_completed_futures()
        future = self._delegate.submit(fn, *args, **kwargs)
        self._futures.append(future)

        return future

    def shutdown(self):
        self._delegate.shutdown(wait=True)
        self._check_completed_futures()
        assert len(self._futures) == 0

    def _check_completed_futures(self):
        """Fail safe in this case means fail fast. TODO: Add retry logic"""
        for future in self._futures.copy():
            if future.done():
                # Will throw an exception here if the future failed
                future.result()
                self._futures.remove(future)
