import time


class PerformanceTimer:

    def __init__(self):

        self.start_time = None

        self.frame_count = 0

    def start(self):

        self.start_time = time.perf_counter()

        self.frame_count = 0

    def frame_processed(self):

        self.frame_count += 1

    def get_elapsed_time(self):

        if self.start_time is None:

            return 0.0

        return time.perf_counter() - self.start_time

    def get_fps(self):

        elapsed = self.get_elapsed_time()

        if elapsed <= 0:

            return 0.0

        return self.frame_count / elapsed
