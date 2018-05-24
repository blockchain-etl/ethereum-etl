class BaseJob(object):
    def run(self):
        try:
            self._start()
            self._export()
        finally:
            self._end()

    def _start(self):
        pass

    def _export(self):
        pass

    def _end(self):
        pass
