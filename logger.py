# %% Import modules
import sys
import contextlib
import time

# %% Define Tee object that duplicates output to file and screen
class Tee(object):
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
    def write(self, data):
        self.stdout.write(data)
        self.file.write(data)
        self.file.flush()
    def flush(self):
        self.file.flush()
    def close(self):
        self.file.close()

# %% Define context manager that redirects the output
@contextlib.contextmanager
def capture_output(logfile, mode):
    new_stdout = Tee(logfile, mode)
    saved_stdout = sys.stdout
    sys.stdout = new_stdout
    try:
        yield None
    finally:
        sys.stdout.close()
        sys.stdout = saved_stdout

# %% Define timing functions
start_times = {'default': 0.0}

def start_timer(this_timer='default'):
    start_times[this_timer] = time.perf_counter()

def report_timer(this_timer='default'):
    time_taken = time.perf_counter() - start_times[this_timer]
    print(f'Completed in {time_string(time_taken)}')

def time_string(time_taken):
    days = int(time_taken // (24 * 3600))
    time_taken = time_taken % (24 * 3600)
    hours = int(time_taken // 3600)
    time_taken %= 3600
    minutes = int(time_taken // 60)
    time_taken %= 60
    seconds = time_taken
    if minutes == 0 and hours == 0 and days == 0:
        time_string = f"{seconds:0.6f} second{'' if seconds == 1 else 's'}"
    else:
        time_string = f"{seconds:0.0f} second{'' if seconds == 1 else 's'}"
    if minutes > 0:
        time_string = f"{minutes} minute{'s' if minutes > 1 else ''} and {time_string}"
    if hours > 0:
        time_string = f"{hours} hour{'s' if hours > 1 else ''}, {time_string}"
    if days > 0:
        time_string = f"{days} day{'s' if days > 1 else ''}, {time_string}"
    return time_string
