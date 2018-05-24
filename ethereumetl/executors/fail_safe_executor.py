class FailSafeExecutor:

    def __init__(self, delegate):
        self.delegate = delegate
        self.futures = []

    def submit(self, fn, *args, **kwargs):
        self._check_completed_futures()
        future = self.delegate.submit(fn, *args, **kwargs)
        self.futures.append(future)

        return future

    def _check_completed_futures(self):
        """Fail safe in this case means fail fast. TODO: Add retry logic"""
        for future in self.futures.copy():
            if future.done():
                # Will throw an exception here if the future failed
                future.result()
                self.futures.remove(future)

    def shutdown(self):
        self.delegate.shutdown(wait=True)
        self._check_completed_futures()
        assert len(self.futures) == 0
