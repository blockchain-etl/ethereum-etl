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

from blockchainetl.streaming.streamer_adapter_stub import StreamerAdapterStub
from blockchainetl.file_utils import smart_open
from web3 import Web3
from datetime import datetime, timedelta


class Streamer:
    def __init__(
            self,
            blockchain_streamer_adapter=StreamerAdapterStub(),
            last_synced_block_file='last_synced_block.txt',
            lag=0,
            start_block=None,
            end_block=None,
            period_seconds=10,
            block_batch_size=10,
            retry_errors=True,
            pid_file=None):
        self.blockchain_streamer_adapter = blockchain_streamer_adapter
        self.last_synced_block_file = last_synced_block_file
        self.lag = lag
        self.start_block = start_block
        self.end_block = end_block
        self.period_seconds = period_seconds
        self.block_batch_size = block_batch_size
        self.retry_errors = retry_errors
        self.pid_file = pid_file
        self.chain_id_cache = None
        self.chain_id_cache_timestamp = None
        self.chain_id = self.get_chain_id_from_api()
        logging.info(f"Successfully fetched {self.chain_id}")
        if self.start_block is not None or not os.path.isfile(self.last_synced_block_file):
            init_last_synced_block_file((self.start_block or 0) - 1, self.last_synced_block_file, self.chain_id)
        self.last_synced_block, last_chain_id = read_last_synced_block_and_chain_id(self.last_synced_block_file)

        if int(last_chain_id) != int(self.chain_id):
            logging.info(f"Last chain is {last_chain_id} is not the same as {self.chain_id}")
            logging.info(f"{last_chain_id} != {self.chain_id}")
            write_last_synced_block(self.last_synced_block_file, 0, self.chain_id)

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

    def _do_stream(self):        
        
        while True and (self.end_block is None or self.last_synced_block < self.end_block):
            synced_blocks = 0

            try:
                synced_blocks = self._sync_cycle()
            except Exception as e:
                # https://stackoverflow.com/a/4992124/1580227
                logging.exception('An exception occurred while syncing block data.')
                if not self.retry_errors:
                    raise e

            if synced_blocks <= 0:
                logging.info('Nothing to sync. Sleeping for {} seconds...'.format(self.period_seconds))
                time.sleep(self.period_seconds)

    def get_chain_id_from_api(self):
        if self.chain_id_cache is not None and datetime.utcnow() - self.chain_id_cache_timestamp < timedelta(minutes=30):
            return self.chain_id_cache
        
        try:
            w3 = Web3(Web3.HTTPProvider('https://zkevm-rpc.sandbox.imtbl.com/'))
            self.chain_id_cache = w3.eth.chain_id
            self.chain_id_cache_timestamp = datetime.utcnow()
            logging.info(f"Re-fetching chain_id from the API {self.chain_id_cache}")
            return self.chain_id_cache
        except Exception as e:
            logging.error(f"Error fetching chain_id from the API: {str(e)}")
            return None

    def _sync_cycle(self):
        current_block = self.blockchain_streamer_adapter.get_current_block_number()

        target_block = self._calculate_target_block(current_block, self.last_synced_block)
        blocks_to_sync = max(target_block - self.last_synced_block, 0)

        logging.info('Current block {}, target block {}, last synced block {}, blocks to sync {}'.format(
            current_block, target_block, self.last_synced_block, blocks_to_sync))

        if blocks_to_sync != 0:
            self.blockchain_streamer_adapter.export_all(self.last_synced_block + 1, target_block, self.chain_id)
            logging.info('Writing last synced block {} with chain_id {}'.format(target_block, self.chain_id))
            write_last_synced_block(self.last_synced_block_file, target_block, self.chain_id)
            self.last_synced_block = target_block
        
        _, last_chain_id = read_last_synced_block_and_chain_id(self.last_synced_block_file)
        self.chain_id = self.get_chain_id_from_api()
        if int(last_chain_id) != int(self.chain_id) and blocks_to_sync == 0:
            logging.info(f"Last chain ID({int(last_chain_id)}) is not the same as current chain ID({int(self.chain_id)}) and no more blocks to sync from last chain")     
            logging.info(f"Resetting last_synced_block_file.txt to block 0 and new chain id {self.chain_id}")
            write_last_synced_block(self.last_synced_block_file, 0, self.chain_id)
            self.last_synced_block = 0

        return blocks_to_sync

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


def write_last_synced_block(file, last_synced_block, chain_id):
    logging.info(f"Writing write_last_synced_block {last_synced_block}, {chain_id}")
    content = f"last_synced_block={last_synced_block},chain_id={chain_id}"
    write_to_file(file, content)


def init_last_synced_block_file(start_block, last_synced_block_file, chain_id=None):
    """Initialize the last synced block file with block number and optionally chain ID."""
    if os.path.isfile(last_synced_block_file):
        raise ValueError(
            f'{last_synced_block_file} should not exist if --start-block option is specified. '
            f'Either remove the {last_synced_block_file} file or the --start-block option.'
        )
    content = f"last_synced_block={start_block}"
    if chain_id:
        content += f",chain_id={chain_id}"
    write_to_file(last_synced_block_file, content)


def read_last_synced_block_and_chain_id(file):
    with smart_open(file, 'r') as file_handle:
        line = file_handle.readline().strip()
        parts = dict(part.split('=') for part in line.split(','))
        last_synced_block = int(parts.get('last_synced_block', 0))
        chain_id = parts.get('chain_id')
        return last_synced_block, chain_id


def write_to_file(file, content):
    logging.info(f"Writing to {file}, with content {content}")
    with smart_open(file, 'w') as file_handle:
        file_handle.write(content)
