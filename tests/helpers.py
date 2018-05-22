def compare_files_ignore_line_order(expected_file_path, actual_file_path):
    with open(expected_file_path) as expected_file, \
            open(actual_file_path) as actual_file:
        expected_lines = expected_file.readlines()
        actual_lines = actual_file.readlines()
        assert len(expected_lines) == len(actual_lines)

        for expected_line, actual_line in zip(sorted(expected_lines), sorted(actual_lines)):
            assert expected_line == actual_line
