def compare_lines_ignore_order(expected, actual):
    expected_lines = expected.splitlines()
    actual_lines = actual.splitlines()
    assert len(expected_lines) == len(actual_lines)

    for expected_line, actual_line in zip(sorted(expected_lines), sorted(actual_lines)):
        assert expected_line == actual_line


def read_file(path):
    with open(path) as file:
        return file.read()
