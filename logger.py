# %% Import modules
import sys
import contextlib
import time

# %% Define Tee object that duplicates output to file and screen
class Tee(object):
    def __init__(self, name, mode, stdout=None):
        self.file = open(name, mode)
        if stdout is None:
            self.stdout = sys.stdout
        else:
            self.stdout = stdout
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
def capture_output(logfile, mode, capture='both'):
    if capture not in ['out', 'err', 'both']:
        raise ValueError(f"Invalid capture setting: {capture}\n"
                          "Valid settings are 'out', 'err', or 'both'.")
    if capture == 'both' and mode == 'w':
        with open(logfile, 'w'):
            pass
        mode = 'a'
    saved_stdout = sys.stdout
    saved_stderr = sys.stderr
    if capture in ['out', 'both']:
        new_stdout = Tee(logfile, mode, stdout=sys.stdout)
        sys.stdout = new_stdout
    if capture in ['err', 'both']:
        new_stderr = Tee(logfile, mode, stdout=sys.stderr)
        sys.stderr = new_stderr
    try:
        yield None
    finally:
        if capture in ['out', 'both']:
            new_stdout.close()
        if capture in ['err', 'both']:
            new_stderr.close()
        sys.stdout = saved_stdout
        sys.stderr = saved_stderr

# %% Define Timer object that keeps a track of start and stop times
class Timer(object):
    def __init__(self):
        self.start_time = None
        self.stop_time = None
    def start(self):
        self.start_time = time.perf_counter()
        self.stop_time = None
    def stop(self):
        if not self.is_running():
            raise IndexError(f'Timer not running.')
        self.stop_time = time.perf_counter()
    def is_running(self):
        return self.start_time is not None and self.stop_time is None
    def is_stopped(self):
        return self.start_time is not None and self.stop_time is not None
    def elapsed_seconds(self):
        if self.is_stopped():
            return self.stop_time - self.start_time
        elif self.is_running():
            return time.perf_counter() - self.start_time
        elif self.start_time is None:
            raise ValueError(f'Timer has not started.')
        else:
            raise ValueError(f'Timer could not report elapsed time.')
    def elapsed(self):
        return time_string(self.elapsed_seconds())

# %% Create private list of existing timers
default_timer = 'default'
_timers = {}
_timers.update({default_timer: Timer()})

# %% Define timing functions
def add_timer(name, this_timer=None):
    if not isinstance(name, str):
        raise ValueError(f"Invalid timer name: '{name}'")
    if name in _timers:
        raise IndexError(f"Time named '{name}' already exists.")
    if this_timer is None:
        this_timer = Timer()
    if not isinstance(this_timer, Timer):
        raise TypeError(f"Invalid object for timer: {this_timer}.")
    _timers.update({name: this_timer})

def get_timer(name):
    if not isinstance(name, str):
        raise ValueError(f"Invalid timer name: '{name}'")
    if name not in _timers:
        raise IndexError(f"No timer named '{name}'")
    return _timers[name]

def start_timer(name=default_timer):
    if not isinstance(name, str):
        raise ValueError(f"Invalid timer name: '{name}'")
    if name not in _timers:
        add_timer(name)
    this_timer = get_timer(name)
    this_timer.start()

def stop_timer(name=default_timer):
    if not isinstance(name, str):
        raise ValueError(f"Invalid timer name: '{name}'")
    if name not in _timers:
        raise IndexError(f"No timer named '{name}'")
    this_timer = get_timer(name)
    this_timer.stop()

def report_timer(name=default_timer):
    if not isinstance(name, str):
        raise ValueError(f"Invalid timer name: '{name}'")
    if name not in _timers:
        raise IndexError(f"No timer named '{name}'")
    this_timer = get_timer(name)
    time_string = this_timer.elapsed()
    return f'Completed in {time_string}'

def remove_timer(name):
    if not isinstance(name, str):
        raise ValueError(f"Invalid timer name: '{name}'")
    if name == default_timer:
        raise ValueError(f"Cannot remove default timer.")
    if name not in _timers:
        raise IndexError(f"No timer named '{name}'")
    del _timers[name]

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

# %% Define context manager that times the contents
@contextlib.contextmanager
def timed():
    this_timer = Timer()
    print('Starting timer...')
    this_timer.start()
    try:
        yield None
    finally:
        this_timer.stop()
        print(f'Completed in {this_timer.elapsed()}')
