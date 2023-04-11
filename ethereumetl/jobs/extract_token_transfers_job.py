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

import time
from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.mappers.token_transfer_mapper import EthTokenTransferMapper
from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.mappers.transaction_mapper import EthTransactionMapper
from ethereumetl.service.token_transfer_extractor import EthTokenTransferExtractor
from multicall import Call, Multicall
import requests


class ExtractTokenTransfersJob(BaseJob):
    def __init__(
            self,
            logs_iterable,
            batch_size,
            max_workers,
            item_exporter,
            transactions_iterable=None,
        ):
        self.logs_iterable = logs_iterable
        self.transactions_iterable = transactions_iterable if transactions_iterable is not None else []

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.receipt_log_mapper = EthReceiptLogMapper()
        self.token_transfer_mapper = EthTokenTransferMapper()
        self.token_transfer_extractor = EthTokenTransferExtractor()
        self.transactions_mapper = EthTransactionMapper()   

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(self.logs_iterable, self._extract_transfers)
        self.batch_work_executor.execute(self.transactions_iterable, self._extract_transfers_from_txn)

    def _extract_transfers(self, log_dicts):        
        for log_dict in log_dicts:
            self._extract_transfer(log_dict)

    def _extract_transfers_from_txn(self, transaction_dicts):        
        for transaction_dict in transaction_dicts:
            txn_hash = transaction_dict.get('hash')
            txn_logs = [log_dict for log_dict in self.logs_iterable if log_dict['transaction_hash'].lower() == txn_hash.lower()]
            self._extract_transfer_from_txn(transaction_dict, txn_logs)

    def _extract_transfer_from_txn(self, transaction_dict, txn_logs):
        token_transfer = self.token_transfer_extractor.extract_transfer_from_transaction(transaction_dict, txn_logs)
        if token_transfer is not None:
            self.item_exporter.export_item(self.token_transfer_mapper.token_transfer_to_dict(token_transfer))

    def _extract_transfer(self, log_dict):
        log = self.receipt_log_mapper.dict_to_receipt_log(log_dict)
        txn = [txn_dict for txn_dict in self.transactions_iterable if txn_dict['hash'].lower() == log.transaction_hash.lower()]
        log.block_timestamp = txn[0]['block_timestamp']
        token_transfer = self.token_transfer_extractor.extract_transfer_from_log(log)
        if token_transfer is not None:
            self.item_exporter.export_item(self.token_transfer_mapper.token_transfer_to_dict(token_transfer))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()

    def _call_back(self, success, value):
        """
        Callback to process results from multicall for a function.
        If call fails returns False (if changed to string throws error)
        """
        try:
            if success is True and isinstance(value, bytes):
                return value.decode("utf-8")
            elif success is True:
                return value
            else:
                return None
        except Exception as e:
            return None


    def add_extra_columns_in_token_transfers(self, token_transfers, web3):

        updated_token_transfers = []
        grouped_token_transfers = {}

        for item in token_transfers:
            block_number = item['block_number']
            if block_number in grouped_token_transfers:
                grouped_token_transfers[block_number].append(item)
            else:
                grouped_token_transfers[block_number] = [item]

        for block_number, transfers in grouped_token_transfers.items():
            
            token_addresses = {}
            multicall_balance_of_calls = []
            for transfer in transfers:
                token_addresses[transfer['token_address']] = ''
                multicall_balance_of_calls.append(
                    Call(
                        transfer['token_address'], 
                        ['balanceOf(address)(uint256)', transfer['from_address']], 
                        [(f"{transfer['from_address']}.balanceOf", self._call_back)]
                    )
                )

            multicall_token_details_calls = []
            unique_token_addresses = list(token_addresses)
            for token_address in unique_token_addresses:
                multicall_token_details_calls.extend(
                    [
                        Call(
                            token_address, 
                            ['totalSupply()(uint256)'],
                            [(f"{token_address}.totalSupply", self._call_back)]
                        ),
                        Call(
                            token_address, 
                            ['decimals()(uint8)'],
                            [(f"{token_address}.decimals", self._call_back)]
                        ),
                        Call(
                            token_address, 
                            ['symbol()(string)'],
                            [(f"{token_address}.symbol", self._call_back)]
                        )
                    ]
                )

            token_address_groups = [unique_token_addresses[i:i+5] for i in range(0, len(unique_token_addresses), 5)]

            block_timestamp = transfers[0]['block_timestamp']
            if time.time() - block_timestamp > 3600 * 6:
                defillama_url = f"https://coins.llama.fi/prices/historical/{block_timestamp}/"
            else:
                defillama_url = "https://coins.llama.fi/prices/current/"
                        
            token_price_dict = {}

            for group in token_address_groups:
                request_url = defillama_url + ','.join([f"ethereum:{address}" for address in group])
                response = requests.get(request_url)

                if response.status_code == 200:
                    coins = response.json()['coins']
                    for key, value in coins.items():
                        address = key[len("ethereum:"):].lower()
                        token_price_dict[address] = value['price']

            previous_block = block_number - 1 if block_number != 0 else 0

            balance_of_multi_call = Multicall(multicall_balance_of_calls, _w3=web3, require_success=False, block_id=previous_block)
            balance_of_multicall_result = balance_of_multi_call()

            token_details_multi_call = Multicall(multicall_token_details_calls, _w3=web3, require_success=False, block_id=previous_block)
            token_details_multicall_result = token_details_multi_call()

            for transfer in transfers:
                
                token_address = transfer['token_address']

                previous_block_balance_of = balance_of_multicall_result[f"{transfer['from_address']}.balanceOf"]
                previous_block_total_supply = token_details_multicall_result[f"{token_address}.totalSupply"]
                token_symbol = token_details_multicall_result[f"{token_address}.symbol"]
                token_decimals = token_details_multicall_result[f"{token_address}.decimals"]

                if token_address in token_price_dict: token_price = token_price_dict[token_address] 
                else: token_price = 0

                updated_token_transfers.append({
                    **transfer,
                    'previous_block_token_balance_of': previous_block_balance_of,
                    'previous_block_token_total_supply': previous_block_total_supply,
                    'symbol': token_symbol,
                    'decimals': token_decimals,
                    'price': token_price
                })
        
        return updated_token_transfers