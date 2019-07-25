# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import json

import pytest


def sort_json(json_string):
    return json.dumps(json.loads(json_string), sort_keys=True)


def compare_lines_ignore_order(expected, actual):
    expected_lines = expected.splitlines()
    actual_lines = actual.splitlines()
    assert len(expected_lines) == len(actual_lines)

    try:
        expected_lines = [sort_json(line) for line in expected_lines]
        actual_lines = [sort_json(line) for line in actual_lines]
    except json.decoder.JSONDecodeError:
        pass

    for expected_line, actual_line in zip(sorted(expected_lines), sorted(actual_lines)):
        assert expected_line == actual_line


def read_file(path):
    if not os.path.exists(path):
        return ''
    with open(path) as file:
        return file.read()


run_slow_tests_variable = os.environ.get('ETHEREUM_ETL_RUN_SLOW_TESTS', 'False')
run_slow_tests = run_slow_tests_variable.lower() in ['1', 'true', 'yes']


def skip_if_slow_tests_disabled(data):
    return pytest.param(*data, marks=pytest.mark.skipif(not run_slow_tests, reason='Skipping slow running tests'))
