# %% Import modules
import sys
import contextlib

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
