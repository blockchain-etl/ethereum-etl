# https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072

import sys
import csv


def set_max_field_size_limit():
    max_int = sys.maxsize
    decrement = True
    while decrement:
        # decrease the maxInt value by factor 10
        # as long as the OverflowError occurs.

        decrement = False
        try:
            csv.field_size_limit(max_int)
        except OverflowError:
            max_int = int(max_int / 10)
            decrement = True
