import os


def read_resource(groups, file_name):
    current_file_dir = os.path.dirname(__file__)
    fixture_file_name = os.path.join(current_file_dir, *groups, file_name)

    if not os.path.exists(fixture_file_name):
        raise ValueError('File does not exist: ' + fixture_file_name)

    with open(fixture_file_name) as file_handle:
        return file_handle.read()
