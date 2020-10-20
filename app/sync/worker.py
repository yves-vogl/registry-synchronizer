#
# Copyright (c) 2020 Yves Vogl
#

import threading
import time


class Worker:

    def __init__(self, concurrent_runs=5):

        self._concurrent_runs = concurrent_runs
        self._jobs = []
        self._threads = []
        self._wait = 0

    def add(self, jobs):

        if isinstance(jobs, list):
            self._jobs += jobs
        else:
            self._jobs.append(jobs)

    @property
    def pending(self):
        return len(self._jobs)

    @property
    def concurrent_runs(self):
        return self._concurrent_runs

    @concurrent_runs.setter
    def concurrent_runs(self, value):
        self._concurrent_runs = value

    def run(self):

        while self.pending > 0:

            print(f'Pending jobs: {self.pending}')
            t = None
            for concurrency in range(self._concurrent_runs):
                if self.pending > 0:
                    t = threading.Thread(target=self._jobs.pop())
                    self._threads.append(t)
                    time.sleep(self._wait)
                    t.start()
                else:
                    break
            t.join()
