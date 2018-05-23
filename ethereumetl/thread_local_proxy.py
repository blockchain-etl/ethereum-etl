import threading


class ThreadLocalProxy:
    def __init__(self, delegate_factory):
        self._thread_local = threading.local()
        self._delegate_factory = delegate_factory

    def __getattr__(self, name):
        return getattr(self._get_thread_local_delegate(), name)

    def _get_thread_local_delegate(self):
        if getattr(self._thread_local, '_delegate', None) is None:
            self._thread_local._delegate = self._delegate_factory()
        return self._thread_local._delegate
