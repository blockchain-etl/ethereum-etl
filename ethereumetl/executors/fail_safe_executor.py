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
