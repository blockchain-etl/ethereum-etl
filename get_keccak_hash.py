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


import argparse

from eth_utils import keccak

from ethereumetl.file_utils import smart_open
from ethereumetl.logging_utils import logging_basic_config

logging_basic_config()

parser = argparse.ArgumentParser(description='Outputs the 32-byte keccak hash of the given string.')
parser.add_argument('-i', '--input-string', default='Transfer(address,address,uint256)', type=str,
                    help='String to hash, e.g. Transfer(address,address,uint256)')
parser.add_argument('-o', '--output', default='-', type=str, help='The output file. If not specified stdout is used.')

args = parser.parse_args()

hash = keccak(text=args.input_string)

with smart_open(args.output, 'w') as output_file:
    output_file.write('0x{}\n'.format(hash.hex()))
