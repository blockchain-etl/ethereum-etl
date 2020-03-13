#  MIT License
#
#  Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

# MIT License
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:


class ListFieldItemConverter:

    def __init__(self, field, new_field_prefix, fill=0, fill_with=None):
        self.field = field
        self.new_field_prefix = new_field_prefix
        self.fill = fill
        self.fill_with = fill_with

    def convert_item(self, item):
        if not item:
            return item

        lst = item.get(self.field)
        result = item
        if lst is not None and isinstance(lst, list):
            result = item.copy()
            del result[self.field]
            for lst_item_index, lst_item in enumerate(lst):
                result[self.new_field_prefix + str(lst_item_index)] = lst_item
            if len(lst) < self.fill:
                for i in range(len(lst), self.fill):
                    result[self.new_field_prefix + str(i)] = self.fill_with
        return result
