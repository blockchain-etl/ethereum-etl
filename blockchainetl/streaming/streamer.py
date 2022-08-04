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


import logging
import os
import time
import traceback

from blockchainetl.streaming.streamer_adapter_stub import StreamerAdapterStub
from blockchainetl.file_utils import smart_open, get_s3
from hypernative.utils import timer

DEAD_LETTER_PREFIX = 'dead_letter'


class Streamer:
    def __init__(
            self,
            blockchain_streamer_adapter: StreamerAdapterStub = StreamerAdapterStub(),
            job_path_prefix='./',
            node_index=0,
            lag=0,
            start_block=None,
            end_block=None,
            period_seconds=10,
            block_batch_size=10,
            retry_errors=True,
            pid_file=None):
        self.blockchain_streamer_adapter = blockchain_streamer_adapter
        self.last_synced_block_file = f'{job_path_prefix}/{node_index}/last_synced_block.txt'
        self.dead_letter_prefix = f'{job_path_prefix}/{DEAD_LETTER_PREFIX}'
        self.lag = lag
        self.start_block = start_block
        self.end_block = end_block
        self.period_seconds = period_seconds
        self.block_batch_size = block_batch_size
        self.retry_errors = retry_errors
        self.pid_file = pid_file

        # TODO: make sure this logic is well - if start/end block are none - remove from last synced prefix?
        if self.start_block is not None or not last_synced_block_file_exists(self.last_synced_block_file):
            init_last_synced_block_file((self.start_block or 0) - 1, self.last_synced_block_file)

        self.last_synced_block = read_last_synced_block(self.last_synced_block_file)

    def stream(self):
        try:
            if self.pid_file is not None:
                logging.info('Creating pid file {}'.format(self.pid_file))
                write_to_file(self.pid_file, str(os.getpid()))
            self.blockchain_streamer_adapter.open()
            self._do_stream()
        finally:
            self.blockchain_streamer_adapter.close()
            if self.pid_file is not None:
                logging.info('Deleting pid file {}'.format(self.pid_file))
                delete_file(self.pid_file)

    @timer
    def _do_stream(self):
        logging.info(f'Starting to stream, '
                     f'last_synced_block [{self.last_synced_block}], '
                     f'end_block [{self.end_block}],'
                     f'block_batch_size [{self.block_batch_size}]')
        while True and (self.end_block is None or self.last_synced_block < self.end_block):
            try:
                synced_blocks = self._sync_cycle()
                if synced_blocks <= 0:
                    logging.info('Nothing to sync. Sleeping for {} seconds...'.format(self.period_seconds))
                    time.sleep(self.period_seconds)
            except Exception as e:
                # https://stackoverflow.com/a/4992124/1580227
                logging.exception('An exception occurred while syncing block data.')
                if not self.retry_errors:
                    raise e
                time.sleep(1)

    def _sync_cycle(self):
        current_block = self.blockchain_streamer_adapter.get_current_block_number()
        if self.last_synced_block == -1:
            self.last_synced_block = current_block - self.lag - 1

        target_block = self._calculate_target_block(current_block, self.last_synced_block)
        blocks_to_sync = max(target_block - self.last_synced_block, 0)

        logging.info('Current block {}, end block {}, target block {}, last synced block {}, blocks to sync {}'.format(
            current_block, self.end_block, target_block, self.last_synced_block, blocks_to_sync))

        if blocks_to_sync != 0:
            self._perform_cycle(target_block, blocks_to_sync)
        return blocks_to_sync

    def _perform_cycle(self, target_block, blocks_to_sync):
        start_time = time.perf_counter()
        try:
            self.blockchain_streamer_adapter.export_all(self.last_synced_block + 1, target_block)
            logging.info('Writing last synced block {}'.format(target_block))
            write_last_synced_block(self.last_synced_block_file, target_block)
            self.last_synced_block = target_block
        except Exception as e:
            logging.error(f'Got an error trying to process - '
                          f'last synced block [{self.last_synced_block}] to target block [{target_block}] - '
                          f'error: {e}\ntrace:{traceback.format_exc()}'
                          f'\nWriting to the dead letter folder and skipping to next batch.')
            write_to_dead_letter(
                dead_letter_prefix=self.dead_letter_prefix,
                start_block=target_block - blocks_to_sync + 1,
                end_block=target_block
            )
        logging.info('Took [{:.5f}] seconds for blocks [{} - {}]'.format(
            time.perf_counter() - start_time,
            target_block - blocks_to_sync + 1,
            target_block
        ))

    def _calculate_target_block(self, current_block, last_synced_block):
        target_block = current_block - self.lag
        target_block = min(target_block, last_synced_block + self.block_batch_size)
        target_block = min(target_block, self.end_block) if self.end_block is not None else target_block
        return target_block


def delete_file(file):
    try:
        os.remove(file)
    except OSError:
        pass


def write_last_synced_block(file, last_synced_block):
    write_to_file(file, str(last_synced_block) + '\n')


def write_to_dead_letter(dead_letter_prefix, start_block, end_block):
    write_to_file(f'{dead_letter_prefix}/'
                  f'start_block-{start_block}_end_block-{end_block}', '')


def last_synced_block_file_exists(last_synced_block_file):
    is_s3 = last_synced_block_file.startswith(r's3://')
    return os.path.isfile(last_synced_block_file) if not is_s3 else get_s3().exists(last_synced_block_file)


def init_last_synced_block_file(start_block, last_synced_block_file):
    if last_synced_block_file_exists(last_synced_block_file):
        logging.warning(
            f'{last_synced_block_file} exists and --start-block option is specified. '
            f'Computation will start from the file mentioned offset.')
    else:
        write_last_synced_block(last_synced_block_file, start_block)


def read_last_synced_block(file):
    with smart_open(file, 'r') as last_synced_block_file:
        return int(last_synced_block_file.read())


def write_to_file(file, content):
    with smart_open(file, 'w') as file_handle:
        file_handle.write(content)
