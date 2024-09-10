import time
#класс секундомера
def format_time(minutes, seconds, milliseconds):
    return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

class Stopwatch:
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0
        self.value_time = 0

    def start(self):
        if self.start_time is None:
            self.start_time = time.time() - self.elapsed_time

    def stop(self):
        if self.start_time is not None:
            self.elapsed_time = time.time() - self.start_time
            self.start_time = None

    def reset(self):
        self.start_time = None
        self.elapsed_time = 0

    def get_time(self):
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
        else:
            elapsed = self.elapsed_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        milliseconds = int((elapsed - int(elapsed)) * 1000)
        self.value_time = minutes * 100000 + seconds * 1000 + milliseconds
        return format_time(minutes, seconds, milliseconds)