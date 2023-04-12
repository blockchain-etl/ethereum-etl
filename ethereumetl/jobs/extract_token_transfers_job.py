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

import json
import time
from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.json_rpc_requests import generate_get_balance_json_rpc, generate_get_code_json_rpc
from ethereumetl.mappers.token_transfer_mapper import EthTokenTransferMapper
from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.mappers.transaction_mapper import EthTransactionMapper
from ethereumetl.service.token_transfer_extractor import EthTokenTransferExtractor
from ethereumetl.utils import hex_to_dec, rpc_response_batch_to_results
from ethereumetl.web3_utils import build_web3
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


    def add_extra_columns_in_token_transfers(self, token_transfers, batch_web3_provider):

        web3 = build_web3(batch_web3_provider)

        updated_token_transfers = []
        grouped_token_transfers = {}

        for item in token_transfers:
            block_number = item['block_number']
            if block_number in grouped_token_transfers:
                grouped_token_transfers[block_number].append(item)
            else:
                grouped_token_transfers[block_number] = [item]

        for block_number, transfers in grouped_token_transfers.items():
            
            previous_block = block_number - 1 if block_number != 0 else 0

            token_addresses = {}
            multicall_previous_block_calls = []
            multicall_current_block_calls = []

            eth_get_balance_addresses = []

            for transfer in transfers:
                token_addresses[transfer['token_address']] = ''

                token_address = transfer['token_address'].lower()
                from_address = transfer['from_address'].lower()

                # if the token is the native currency i.e ETH, then we have to call eth_getBalance and not balanceOf
                if token_address.lower() == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'.lower():
                    eth_get_balance_addresses.append(from_address)

                # else since the token is an ERC token, we call balanceOf
                else:
                    # balanceOf for previous block
                    multicall_previous_block_calls.append(
                        Call(
                            token_address, 
                            ['balanceOf(address)(uint256)', from_address], 
                            [(f"{token_address}.balanceOf.{from_address}", self._call_back)]
                        ),
                    )
                    # balanceOf for current block
                    multicall_current_block_calls.append(
                        Call(
                            token_address, 
                            ['balanceOf(address)(uint256)', from_address], 
                            [(f"{token_address}.balanceOf.{from_address}", self._call_back)]
                        ),
                    )

            unique_token_addresses = list(token_addresses)
            for unique_token_address in unique_token_addresses:
                token_address = unique_token_address.lower()

                # totalSupply() for previous block
                multicall_previous_block_calls.append(
                    Call(
                        token_address, 
                        ['totalSupply()(uint256)'],
                        [(f"{token_address}.totalSupply", self._call_back)]
                    ),
                )
                multicall_current_block_calls.extend(
                    [
                        # totalSupply() for current block
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


            previous_block_multi_call = Multicall(multicall_previous_block_calls, _w3=web3, require_success=False, block_id=previous_block)
            previous_block_multicall_result = previous_block_multi_call()

            current_block_multi_call = Multicall(multicall_current_block_calls, _w3=web3, require_success=False)
            current_block_multicall_result = current_block_multi_call()

            # get token prices from defillama
            token_price_dict = self._get_price_from_defillama(unique_token_addresses, transfers[0]['block_timestamp'])

            # get eth_getBalance for `from` addresses using RPC for previous block and current block
            eth_get_balance_result_before = self._get_eth_balance_for_addresses(batch_web3_provider, eth_get_balance_addresses, previous_block)
            eth_get_balance_result_after = self._get_eth_balance_for_addresses(batch_web3_provider, eth_get_balance_addresses, block_number)
           
            for transfer in transfers:
                
                token_address = transfer['token_address'].lower()
                from_address = transfer['from_address'].lower()

                # if its eth transfer, we fetch details from eth_getBalance RPC
                if (token_address == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'):
                    balance_of_from_before = eth_get_balance_result_before[from_address]
                    balance_of_from_after = eth_get_balance_result_after[from_address]
                # else we fetch it form token.balanceOf contract method call
                else:
                    balance_of_from_before = previous_block_multicall_result[f"{token_address}.balanceOf.{from_address}"]
                    balance_of_from_after = current_block_multicall_result[f"{token_address}.balanceOf.{from_address}"]

                total_supply_before = previous_block_multicall_result[f"{token_address}.totalSupply"]
                total_supply_after = current_block_multicall_result[f"{token_address}.totalSupply"]
                token_symbol = current_block_multicall_result[f"{token_address}.symbol"]
                token_decimals = current_block_multicall_result[f"{token_address}.decimals"]

                if token_address in token_price_dict: token_price = token_price_dict[token_address] 
                else: token_price = 0

                updated_token_transfers.append({
                    **transfer,
                    'balance_of_from_before': balance_of_from_before,
                    'balance_of_from_after': balance_of_from_after,
                    'total_supply_before': total_supply_before,
                    'total_supply_after': total_supply_after,
                    'symbol': token_symbol,
                    'decimals': token_decimals,
                    'price': token_price
                })
        
        return updated_token_transfers

    def _get_price_from_defillama(self, token_addresses, timestamp):
        token_address_groups = [token_addresses[i:i+5] for i in range(0, len(token_addresses), 5)]

        if time.time() - timestamp > 3600 * 6:
            defillama_url = f"https://coins.llama.fi/prices/historical/{timestamp}/"
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
        return token_price_dict

    def _get_eth_balance_for_addresses(self, batch_web3_provider, addresses, block_number):

        get_balance_rpc = list(generate_get_balance_json_rpc(addresses, block_number))
        response_batch = batch_web3_provider.make_batch_request(json.dumps(get_balance_rpc))  
        responses = list(response_batch)

        responses_dict = {}

        for response in responses:
            id = response['id']
            responses_dict[id] = response['result']

        result = {}

        for request in get_balance_rpc:
            id = request['id']
            address = request['params'][0]
            result[address] = hex_to_dec(responses_dict[id])

        return result