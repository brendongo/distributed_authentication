import time
import json


class Timer(object):
    def __init__(self, num_calls, filename):
        time.sleep(1)
        self._num_calls = num_calls
        self._start = time.time()
        self._calls = []

    def call(self, msg):
        self._num_calls -= 1
        self._calls.append(time.time() - self._start)
        if self._num_calls == 0:
            end = time.time()
            total_time = end - self._start
            print "{} TOTAL TIME: {} {}".format(
                    "=" * 20, total_time, "=" * 20)
            with open(self._filename, "w") as f:
                f.write(json.dumps(self._calls))
