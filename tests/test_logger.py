# Tests logger.py

import pytest
import sys
import pathlib
import time
import re
from contextlib import nullcontext as does_not_raise

import logger

# Main test class
class TestLogger:

    # Custom fixtures
    @pytest.fixture(autouse=True)
    def reset_timers(self):
        initial_timers = logger._timers.copy()
        yield None
        logger._timers = initial_timers.copy()

    # Parameter sets for testing logging
    log_modes = ['w', 'a']
    log_names = ['test.log', 'log.txt', 'log_file', 'long log file name.log']
    log_outputs = ['default', 'sys.stdout', 'sys.stderr']
    log_messages = ['Hello world!',
                    'Hello world!\n',
                    'Line 1\nLine 2\nLine 3',
                    'Line 1\nLine 2\nLine 3\n']

    # Helper functions
    def get_output(self, capsys, output):
        if output in ['default', 'sys.stdout']:
            return capsys.readouterr().out
        elif output == 'sys.stderr':
            return capsys.readouterr().err
        else:
            raise ValueError(f'Invalid output type: {output}')

    # Tests for Tee object
    @pytest.mark.parametrize('output', log_outputs)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_return_type(self, name, mode, output, tmp_path):
        filename = tmp_path.joinpath(name)
        if output == 'default':
            test_object = logger.Tee(filename, mode)
        else:
            test_object = logger.Tee(filename, mode, stdout=eval(output))
        assert isinstance(test_object, logger.Tee)

    @pytest.mark.parametrize('output', log_outputs)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_filename(self, name, mode, output, tmp_path):
        filename = tmp_path.joinpath(name)
        if output == 'default':
            test_object = logger.Tee(filename, mode)
        else:
            test_object = logger.Tee(filename, mode, stdout=eval(output))
        assert test_object.file.name == str(filename)

    @pytest.mark.parametrize('output', log_outputs)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_filemode(self, name, mode, output, tmp_path):
        filename = tmp_path.joinpath(name)
        if output == 'default':
            test_object = logger.Tee(filename, mode)
        else:
            test_object = logger.Tee(filename, mode, stdout=eval(output))
        assert test_object.file.mode == str(mode)
        if mode in ['w', 'a']:
            assert test_object.file.seekable() == True
            assert test_object.file.writable() == True
            assert test_object.file.readable() == False
            assert test_object.file.closed == False

    @pytest.mark.parametrize('output', log_outputs)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_stdout(self, name, mode, output, tmp_path):
        filename = tmp_path.joinpath(name)
        if output == 'default':
            test_object = logger.Tee(filename, mode)
            assert test_object.stdout == sys.stdout
        else:
            test_object = logger.Tee(filename, mode, stdout=eval(output))
            assert test_object.stdout == eval(output)

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('output', log_outputs)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_write(self, name, mode, output, message, tmp_path, capsys):
        """Tee.write() should write to stdout and to file."""
        filename = tmp_path.joinpath(name)
        if output == 'default':
            test_object = logger.Tee(filename, mode)
        else:
            test_object = logger.Tee(filename, mode, stdout=eval(output))
        test_object.write(message)
        assert self.get_output(capsys, output) == message
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        expected = message.split('\n')
        if expected[-1] == '':
            expected = expected[:-1]
        assert test_message == expected

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('output', log_outputs)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_append(self, name, output, message, tmp_path, capsys):
        """Write once then append the same message again."""
        filename = tmp_path.joinpath(name)
        if output == 'default':
            test_object = logger.Tee(filename, 'w')
        else:
            test_object = logger.Tee(filename, 'w', stdout=eval(output))
        test_object.write(message)
        test_object.close()
        if output == 'default':
            test_object = logger.Tee(filename, 'a')
        else:
            test_object = logger.Tee(filename, 'a', stdout=eval(output))
        test_object.write(message)
        test_object.close()
        assert self.get_output(capsys, output) == message + message
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        expected = (message + message).split('\n')
        if expected[-1] == '':
            expected = expected[:-1]
        assert test_message == expected

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('output', log_outputs)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_overwrite(self, name, output, message, tmp_path, capsys):
        """Write once then overwrite the file."""
        filename = tmp_path.joinpath(name)
        if output == 'default':
            test_object = logger.Tee(filename, 'w')
        else:
            test_object = logger.Tee(filename, 'w', stdout=eval(output))
        test_object.write(message)
        test_object.close()
        if output == 'default':
            test_object = logger.Tee(filename, 'w')
        else:
            test_object = logger.Tee(filename, 'w', stdout=eval(output))
        test_object.write(message)
        test_object.close()
        assert self.get_output(capsys, output) == message + message
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        expected = message.split('\n')
        if expected[-1] == '':
            expected = expected[:-1]
        assert test_message == expected

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('output', log_outputs)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_flush(self, name, mode, output, message, tmp_path, capsys):
        """Tee.write() already includes a flush, so this just checks for errors."""
        # Create object
        filename = tmp_path.joinpath(name)
        if output == 'default':
            test_object = logger.Tee(filename, mode)
        else:
            test_object = logger.Tee(filename, mode, stdout=eval(output))
        # Write contents
        test_object.write(message)
        # Save state before flush
        _ = self.get_output(capsys, output)
        with open(filename, 'r') as f:
            file_before = f.readlines()
        # Test flush
        with does_not_raise():
            test_object.flush()
        # Get state after flush
        stdout_after = self.get_output(capsys, output)
        with open(filename, 'r') as f:
            file_after = f.readlines()
        # Assert no new output
        assert stdout_after == ''
        assert file_after == file_before

    @pytest.mark.parametrize('output', log_outputs)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_close(self, name, mode, output, tmp_path):
        filename = tmp_path.joinpath(name)
        if output == 'default':
            test_object = logger.Tee(filename, mode)
        else:
            test_object = logger.Tee(filename, mode, stdout=eval(output))
        assert test_object.file.closed == False
        test_object.close()
        assert test_object.file.closed == True


    # Tests for capture_output() context
    log_capture = ['default', 'out', 'err', 'both']

    @pytest.mark.parametrize('capture', log_capture)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_filename(self, name, mode, capture, tmp_path):
        filename = tmp_path.joinpath(name)
        assert not filename.is_file()
        if capture == 'default':
            with logger.capture_output(filename, mode):
                pass
        else:
            with logger.capture_output(filename, mode, capture=capture):
                pass
        assert filename.is_file()

    @pytest.mark.parametrize('capture', log_capture)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_stdout(self, name, mode, capture, tmp_path):
        before = sys.stdout
        filename = tmp_path.joinpath(name)
        assert not filename.is_file()
        if capture == 'default':
            with logger.capture_output(filename, mode):
                pass
        else:
            with logger.capture_output(filename, mode, capture=capture):
                pass
        assert sys.stdout == before

    @pytest.mark.parametrize('capture', log_capture)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_stderr(self, name, mode, capture, tmp_path):
        before = sys.stderr
        filename = tmp_path.joinpath(name)
        assert not filename.is_file()
        if capture == 'default':
            with logger.capture_output(filename, mode):
                pass
        else:
            with logger.capture_output(filename, mode, capture=capture):
                pass
        assert sys.stderr == before

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('capture', log_capture)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_print(
            self, name, mode, capture, message, tmp_path, capsys):
        """Printed output should be captured to stdout and to file."""
        filename = tmp_path.joinpath(name)
        if capture == 'default':
            with logger.capture_output(filename, mode):
                print(message)
        else:
            with logger.capture_output(filename, mode, capture=capture):
                print(message)
        assert capsys.readouterr().out == message + '\n' # print adds a newline
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        if capture in ['default', 'out', 'both']:
            expected = message.split('\n')
        else:
            expected = []
        assert test_message == expected

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('capture', log_capture)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_error(
            self, name, mode, capture, message, tmp_path, capsys):
        """Error output should be captured if selected for capture."""
        filename = tmp_path.joinpath(name)
        if capture == 'default':
            with logger.capture_output(filename, mode):
                print(message, file=sys.stderr)
        else:
            with logger.capture_output(filename, mode, capture=capture):
                print(message, file=sys.stderr)
        assert capsys.readouterr().err == message + '\n'
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        if capture in ['default', 'err', 'both']:
            expected = message.split('\n')
        else:
            expected = []
        assert test_message == expected

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('capture', log_capture)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_append(
            self, name, capture, message, tmp_path, capsys):
        """Printed output should be captured to stdout and to file."""
        filename = tmp_path.joinpath(name)
        if capture == 'default':
            with logger.capture_output(filename, 'w'):
                print(message)
        else:
            with logger.capture_output(filename, 'w', capture=capture):
                print(message)
        assert capsys.readouterr().out == message + '\n' # print adds a newline
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        if capture in ['default', 'out', 'both']:
            expected = message.split('\n')
        else:
            expected = []
        assert test_message == expected
        # Now do it again to append the same message another time
        if capture == 'default':
            with logger.capture_output(filename, 'a'):
                print(message)
        else:
            with logger.capture_output(filename, 'a', capture=capture):
                print(message)
        assert capsys.readouterr().out == message + '\n' # captured output since last check
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        if capture in ['default', 'out', 'both']:
            expected = (message + '\n' + message).split('\n')
        else:
            expected = []
        assert test_message == expected

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('capture', log_capture)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_overwrite(
            self, name, capture, message, tmp_path, capsys):
        """Printed output should be captured to stdout and to file."""
        filename = tmp_path.joinpath(name)
        if capture == 'default':
            with logger.capture_output(filename, 'w'):
                print(message)
        else:
            with logger.capture_output(filename, 'w', capture=capture):
                print(message)
        assert capsys.readouterr().out == message + '\n' # print adds a newline
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        if capture in ['default', 'out', 'both']:
            expected = message.split('\n')
        else:
            expected = []
        assert test_message == expected
        # Now do it again to write the same message another time
        if capture == 'default':
            with logger.capture_output(filename, 'w'):
                print(message)
        else:
            with logger.capture_output(filename, 'w', capture=capture):
                print(message)
        assert capsys.readouterr().out == message + '\n' # captured output since last check
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        if capture in ['default', 'out', 'both']:
            expected = message.split('\n')
        else:
            expected = []
        assert test_message == expected


    # Parameters and utility functions for testing timing methods
    default_timer = 'default'
    test_timers = [default_timer, 'test1', 'test 2']
    test_runs = [0.01, 0.02, 0.05, 0.1, 0.2]
    test_times = [(1,         '1.000000 second'),
                  (2,         '2.000000 seconds'),
                  (2.2,       '2.200000 seconds'),
                  (2.123456,  '2.123456 seconds'),
                  (2.0000009, '2.000001 seconds'),
                  (2.1234567, '2.123457 seconds'),
                  (65,        '1 minute and 5 seconds'),
                  (65.9,      '1 minute and 6 seconds'),
                  (65.09,     '1 minute and 5 seconds'),
                  (3600,      '1 hour, 0 seconds'),
                  (3601,      '1 hour, 1 second'),
                  (3646,      '1 hour, 46 seconds'),
                  (3661,      '1 hour, 1 minute and 1 second'),
                  (15286,     '4 hours, 14 minutes and 46 seconds'),
                  (86400,     '1 day, 0 seconds'),
                  (86401,     '1 day, 1 second'),
                  (86461,     '1 day, 1 minute and 1 second'),
                  (90061,     '1 day, 1 hour, 1 minute and 1 second'),
                  (4365432,   '50 days, 12 hours, 37 minutes and 12 seconds')]

    def convert_timestring_to_seconds(self, time_string):
        match = re.search(r'([0-9\.]*) second', time_string)
        seconds = float(match.group(1))
        if 'minute' in time_string:
            match = re.search(r'([0-9]*) minute', time_string)
            seconds += int(match.group(1))*60
        if 'hour' in time_string:
            match = re.search(r'([0-9]*) hour', time_string)
            seconds += int(match.group(1))*60*60
        if 'day' in time_string:
            match = re.search(r'([0-9]*) day', time_string)
            seconds += int(match.group(1))*60*60*24
        return seconds

    # Tests for Timer object
    def test_timer_class_return_type(self):
        timer = logger.Timer()
        assert isinstance(timer, logger.Timer)

    def test_timer_class_initialisation(self):
        timer = logger.Timer()
        assert timer.start_time is None
        assert timer.stop_time is None

    def test_timer_class_standalone(self):
        timer = logger.Timer()
        assert timer not in logger._timers.values()

    def test_timer_class_start_time(self):
        timer = logger.Timer()
        timer.start()
        assert timer.start_time <= time.perf_counter()

    def test_timer_class_is_running(self):
        timer = logger.Timer()
        timer.start()
        result = timer.is_running()
        assert result == True

    def test_timer_class_is_not_running_not_started(self):
        timer = logger.Timer()
        result = timer.is_running()
        assert result == False

    def test_timer_class_is_not_running_stopped(self):
        timer = logger.Timer()
        timer.start()
        time.sleep(0.1)
        timer.stop()
        result = timer.is_running()
        assert result == False

    def test_timer_class_is_stopped(self):
        timer = logger.Timer()
        timer.start()
        time.sleep(0.1)
        timer.stop()
        result = timer.is_stopped()
        assert result == True

    def test_timer_class_is_not_stopped_not_started(self):
        timer = logger.Timer()
        result = timer.is_stopped()
        assert result == False

    def test_timer_class_is_not_stopped_still_running(self):
        timer = logger.Timer()
        timer.start()
        result = timer.is_stopped()
        assert result == False

    def test_timer_class_stop_time(self):
        timer = logger.Timer()
        timer.start()
        time.sleep(0.01)
        timer.stop()
        assert timer.stop_time <= time.perf_counter()

    def test_timer_class_run_time_running(self):
        timer = logger.Timer()
        timer.start()
        time.sleep(0.01)
        assert time.perf_counter() - timer.start_time >= 0.01

    def test_timer_class_run_time_stopped(self):
        timer = logger.Timer()
        timer.start()
        time.sleep(0.01)
        timer.stop()
        time.sleep(0.05)
        assert timer.stop_time - timer.start_time >= 0.01
        assert timer.stop_time - timer.start_time < 0.05

    @pytest.mark.parametrize('run_time', test_runs)
    def test_timer_class_elapsed_seconds_running(self, run_time):
        timer = logger.Timer()
        timer.start()
        time.sleep(run_time)
        result = timer.elapsed_seconds()
        assert round(result, 2) == round(run_time, 2)

    @pytest.mark.parametrize('run_time', test_runs)
    def test_timer_class_elapsed_seconds_stopped(self, run_time):
        timer = logger.Timer()
        timer.start()
        time.sleep(run_time)
        timer.stop()
        time.sleep(0.05)
        result = timer.elapsed_seconds()
        assert round(result, 2) == round(run_time, 2)

    @pytest.mark.parametrize('start', [0.0, 0.1, 1.0, 100000.0])
    @pytest.mark.parametrize('seconds, expected', test_times)
    def test_timer_class_elapsed_seconds_forced(self, start, seconds, expected):
        timer = logger.Timer()
        timer.start_time = start
        timer.stop_time = timer.start_time + seconds
        result = timer.elapsed_seconds()
        assert round(result, 6) == round(seconds, 6)

    @pytest.mark.parametrize('start', [0.0, 0.1, 1.0, 100000.0])
    @pytest.mark.parametrize('seconds, expected', test_times)
    def test_timer_class_elapsed_forced(self, start, seconds, expected):
        timer = logger.Timer()
        timer.start_time = start
        timer.stop_time = timer.start_time + seconds
        result = timer.elapsed()
        assert result == expected

    # Tests for timing methods
    @pytest.mark.parametrize('name', [default_timer])
    def test_timer_defaults(self, name):
        assert name in logger._timers

    @pytest.mark.parametrize('name', [default_timer])
    def test_timer_get_defaults(self, name):
        timer = logger.get_timer(name)
        assert timer is not None

    @pytest.mark.parametrize('name', [default_timer])
    def test_timer_get_defaults_return_type(self, name):
        timer = logger.get_timer(name)
        assert isinstance(timer, logger.Timer)

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_creation(self, name):
        if name != self.default_timer:
            logger.add_timer(name)
        assert name in logger._timers

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_add_created(self, name):
        timer = logger.Timer()
        if name == self.default_timer:
            with pytest.raises(IndexError):
                logger.add_timer(name, timer)
        else:
            logger.add_timer(name, timer)
        assert name in logger._timers

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_get_created(self, name):
        if name != self.default_timer:
            logger.add_timer(name)
        timer = logger.get_timer(name)
        assert timer is not None

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_get_created_return_type(self, name):
        if name != self.default_timer:
            logger.add_timer(name)
        timer = logger.get_timer(name)
        assert isinstance(timer, logger.Timer)

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_get_added(self, name):
        if name != self.default_timer:
            timer = logger.Timer()
            logger.add_timer(name, timer)
        else:
            timer = logger._timers[name]
        result = logger.get_timer(name)
        assert result == timer

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_get_non_existent(self, name):
        if name == self.default_timer:
            condition = does_not_raise()
        else:
            condition = pytest.raises(IndexError)
        with condition:
            logger.get_timer(name)

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_creation_on_start(self, name):
        logger.start_timer(name)
        assert name in logger._timers

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_removal(self, name):
        if name == self.default_timer:
            # Should not be able to remove default timer
            assert name in logger._timers
            with pytest.raises(ValueError):
                logger.remove_timer(name)
            assert name in logger._timers
        else:
            # Add and then remove extra timer
            logger.add_timer(name)
            assert name in logger._timers
            logger.remove_timer(name)
            assert name not in logger._timers

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_start_time(self, name):
        logger.start_timer(name)
        assert logger._timers[name].start_time <= time.perf_counter()

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_get_start_time(self, name):
        logger.start_timer(name)
        timer = logger.get_timer(name)
        assert timer.start_time <= time.perf_counter()

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_stop_time(self, name):
        logger.start_timer(name)
        time.sleep(0.01)
        logger.stop_timer(name)
        assert logger._timers[name].stop_time <= time.perf_counter()

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_get_stop_time(self, name):
        logger.start_timer(name)
        time.sleep(0.01)
        logger.stop_timer(name)
        timer = logger.get_timer(name)
        assert timer.stop_time <= time.perf_counter()

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_run_time_running(self, name):
        logger.start_timer(name)
        time.sleep(0.01)
        assert time.perf_counter() - logger._timers[name].start_time >= 0.01

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_get_run_time_running(self, name):
        logger.start_timer(name)
        time.sleep(0.01)
        timer = logger.get_timer(name)
        assert time.perf_counter() - timer.start_time >= 0.01

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_run_time_stopped(self, name):
        logger.start_timer(name)
        time.sleep(0.01)
        logger.stop_timer(name)
        timer = logger._timers[name]
        time.sleep(0.05)
        assert timer.stop_time - timer.start_time >= 0.01
        assert timer.stop_time - timer.start_time < 0.05

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_get_run_time_stopped(self, name):
        logger.start_timer(name)
        time.sleep(0.01)
        logger.stop_timer(name)
        timer = logger.get_timer(name)
        time.sleep(0.05)
        assert timer.stop_time - timer.start_time >= 0.01
        assert timer.stop_time - timer.start_time < 0.05

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_report_return_type(self, name):
        logger.start_timer(name)
        result = logger.report_timer(name)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_report_value(self, name):
        logger.start_timer(name)
        time.sleep(0.01)
        result = logger.report_timer(name)
        assert self.convert_timestring_to_seconds(result) >= 0.01

    @pytest.mark.parametrize('name', test_timers)
    def test_timer_report_no_stdout(self, name, capsys):
        logger.start_timer(name)
        _ = logger.report_timer(name)
        test_output = capsys.readouterr().out
        assert test_output == ''

    @pytest.mark.parametrize('seconds, expected', test_times)
    def test_timer_time_string(self, seconds, expected):
        test_output = logger.time_string(seconds)
        assert test_output == expected

    # Tests for timed() context
    timed_quiet = ['default', True, False]

    @pytest.mark.parametrize('quiet', timed_quiet)
    def test_timed_start(self, quiet, capsys):
        if quiet == 'default':
            with logger.timed():
                pass
        else:
            with logger.timed(quiet=quiet):
                pass
        if quiet in ['default', False]:
            assert 'Starting timer' in capsys.readouterr().out
        else:
            assert capsys.readouterr().out == ''

    @pytest.mark.parametrize('quiet', timed_quiet)
    def test_timed_completion(self, quiet, capsys):
        if quiet == 'default':
            with logger.timed():
                pass
        else:
            with logger.timed(quiet=quiet):
                pass
        if quiet in ['default', False]:
            assert 'Completed in' in capsys.readouterr().out
        else:
            assert capsys.readouterr().out == ''

    @pytest.mark.parametrize('quiet', timed_quiet)
    @pytest.mark.parametrize('run_time', test_runs)
    def test_timed_runtime(self, run_time, quiet, capsys):
        if quiet == 'default':
            with logger.timed():
                time.sleep(run_time)
        else:
            with logger.timed(quiet=quiet):
                time.sleep(run_time)
        time.sleep(0.05)
        if quiet in ['default', False]:
            result = self.convert_timestring_to_seconds(capsys.readouterr().out)
            assert round(result, 2) == round(run_time, 2)
        else:
            assert capsys.readouterr().out == ''
