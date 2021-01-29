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

    # Parameter sets for testing logging
    log_modes = ['w', 'a']
    log_names = ['test.log', 'log.txt', 'log_file', 'long log file name.log']
    log_messages = ['Hello world!',
                    'Hello world!\n',
                    'Line 1\nLine 2\nLine 3',
                    'Line 1\nLine 2\nLine 3\n']

    # Tests for Tee object
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_return_type(self, name, mode, tmp_path):
        filename = tmp_path.joinpath(name)
        test_object = logger.Tee(filename, mode)
        assert isinstance(test_object, logger.Tee)

    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_filename(self, name, mode, tmp_path):
        filename = tmp_path.joinpath(name)
        test_object = logger.Tee(filename, mode)
        assert test_object.file.name == str(filename)

    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_filemode(self, name, mode, tmp_path):
        filename = tmp_path.joinpath(name)
        test_object = logger.Tee(filename, mode)
        assert test_object.file.mode == str(mode)
        if mode in ['w', 'a']:
            assert test_object.file.seekable() == True
            assert test_object.file.writable() == True
            assert test_object.file.readable() == False
            assert test_object.file.closed == False

    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_stdout(self, name, mode, tmp_path):
        filename = tmp_path.joinpath(name)
        test_object = logger.Tee(filename, mode)
        assert test_object.stdout == sys.stdout

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_write(self, name, mode, message, tmp_path, capsys):
        """Tee.write() should write to stdout and to file."""
        filename = tmp_path.joinpath(name)
        test_object = logger.Tee(filename, mode)
        test_object.write(message)
        assert capsys.readouterr().out == message
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        expected = message.split('\n')
        if expected[-1] == '':
            expected = expected[:-1]
        assert test_message == expected

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_append(self, name, message, tmp_path, capsys):
        """Write once then append the same message again."""
        filename = tmp_path.joinpath(name)
        test_object = logger.Tee(filename, 'w')
        test_object.write(message)
        test_object.close()
        test_object = logger.Tee(filename, 'a')
        test_object.write(message)
        test_object.close()
        assert capsys.readouterr().out == message + message
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        expected = (message + message).split('\n')
        if expected[-1] == '':
            expected = expected[:-1]
        assert test_message == expected

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_flush(self, name, mode, message, tmp_path, capsys):
        """Tee.write() already includes a flush, so this just checks for errors."""
        # Create object
        filename = tmp_path.joinpath(name)
        test_object = logger.Tee(filename, mode)
        # Write contents
        test_object.write(message)
        # Save state before flush
        stdout_before = capsys.readouterr().out
        with open(filename, 'r') as f:
            file_before = f.readlines()
        # Test flush
        with does_not_raise():
            test_object.flush()
        # Get state after flush
        stdout_after = capsys.readouterr().out
        with open(filename, 'r') as f:
            file_after = f.readlines()
        # Assert no new output
        assert stdout_after == ''
        assert file_after == file_before

    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_tee_close(self, name, mode, tmp_path):
        filename = tmp_path.joinpath(name)
        test_object = logger.Tee(filename, mode)
        assert test_object.file.closed == False
        test_object.close()
        assert test_object.file.closed == True


    # Tests for capture_output() method
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_filename(self, name, mode, tmp_path):
        filename = tmp_path.joinpath(name)
        assert not filename.is_file()
        with logger.capture_output(filename, mode):
            pass
        assert filename.is_file()

    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_stdout(self, name, mode, tmp_path):
        before = sys.stdout
        filename = tmp_path.joinpath(name)
        assert not filename.is_file()
        with logger.capture_output(filename, mode):
            pass
        assert sys.stdout == before

    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_stderr(self, name, mode, tmp_path):
        before = sys.stderr
        filename = tmp_path.joinpath(name)
        assert not filename.is_file()
        with logger.capture_output(filename, mode):
            pass
        assert sys.stderr == before

    @pytest.mark.parametrize('message', log_messages)
    @pytest.mark.parametrize('mode', log_modes)
    @pytest.mark.parametrize('name', log_names)
    def test_capture_output_print(self, name, mode, message, tmp_path, capsys):
        """Printed output should be captured to stdout and to file."""
        filename = tmp_path.joinpath(name)
        with logger.capture_output(filename, mode):
            print(message)
        assert capsys.readouterr().out == message + '\n' # print adds a newline
        with open(filename, 'r') as f:
            test_message = [line.strip() for line in f.readlines()]
        expected = message.split('\n')
        assert test_message == expected


    # Parameters and utility functions for testing timing methods
    test_timers = ['default', 'test1', 'test 2']
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

    # Tests for timing methods
    @pytest.mark.parametrize('timer', ['default'])
    def test_timer_default(self, timer):
        assert 'default' in logger.start_times

    @pytest.mark.parametrize('timer', test_timers)
    def test_timer_creation(self, timer):
        logger.start_timer(timer)
        assert timer in logger.start_times

    @pytest.mark.parametrize('timer', test_timers)
    def test_timer_start_time(self, timer):
        logger.start_timer(timer)
        assert logger.start_times[timer] <= time.perf_counter()

    @pytest.mark.parametrize('timer', test_timers)
    def test_timer_run_time(self, timer):
        logger.start_timer(timer)
        time.sleep(0.01)
        assert time.perf_counter() - logger.start_times[timer] >= 0.01

    @pytest.mark.parametrize('timer', test_timers)
    def test_timer_report_return_type(self, timer, capsys):
        logger.start_timer(timer)
        logger.report_timer(timer)
        test_output = capsys.readouterr().out
        assert isinstance(test_output, str)
        assert len(test_output) > 0

    @pytest.mark.parametrize('timer', test_timers)
    def test_timer_report_value(self, timer, capsys):
        logger.start_timer(timer)
        time.sleep(0.01)
        logger.report_timer(timer)
        test_output = capsys.readouterr().out
        assert self.convert_timestring_to_seconds(test_output) >= 0.01

    @pytest.mark.parametrize('seconds, expected', test_times)
    def test_timer_time_string(self, seconds, expected):
        test_output = logger.time_string(seconds)
        assert test_output == expected
