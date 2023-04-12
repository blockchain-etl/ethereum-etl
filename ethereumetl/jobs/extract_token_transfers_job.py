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
import asyncio
import aiohttp
import nest_asyncio

# asyncio does not allow its event loop to be nested. 
# So, when in an environment where the event loop is already running, it’s impossible to run tasks and wait for the result. 
# Trying to do so will give the error “RuntimeError: This event loop is already running”.
# Multicall library has event loop already running, but we want to call it 2 times in parallel.
# So since 1st multicall has event loop running, the 2nd multicall cannot run in parallel, and has to wait for the first to finish
# In order to solve this, we use nest_asyncio
nest_asyncio.apply()

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

            values = asyncio.run(
                self._fetch_details_in_parallel(
                    unique_token_addresses=unique_token_addresses,
                    timestamp=transfers[0]['block_timestamp'], 
                    batch_web3_provider=batch_web3_provider, 
                    eth_get_balance_addresses=eth_get_balance_addresses,
                    previous_block=previous_block,
                    current_block=block_number,
                    previous_block_multicall_calls=multicall_previous_block_calls,
                    current_block_multicall_calls=multicall_current_block_calls,
                    web3=web3,
                    require_success=False,
                )
            )

            previous_block_multicall_result = values[0]
            current_block_multicall_result = values[1]

            token_price_dict = values[2]
            
            eth_get_balance_result_before =values[3]
            eth_get_balance_result_after = values[4]

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

    async def _fetch_details_in_parallel(self, unique_token_addresses, timestamp, batch_web3_provider, eth_get_balance_addresses, previous_block, current_block, previous_block_multicall_calls, current_block_multicall_calls, web3, require_success):
        return await asyncio.gather(
            self._multi_call(previous_block_multicall_calls, web3, require_success, previous_block),
            self._multi_call(current_block_multicall_calls, web3, require_success, current_block),
            self._get_price_from_defillama(unique_token_addresses, timestamp),
            self._get_eth_balance_for_addresses(batch_web3_provider, eth_get_balance_addresses, previous_block),
            self._get_eth_balance_for_addresses(batch_web3_provider, eth_get_balance_addresses, current_block) 
        )

    async def _fetch_price(self, session, url):
        token_price_dict = {}
        async with session.get(url) as response:
            if response.status == 200:
                res = await response.json()
                for key, value in res['coins'].items():
                    address = key[len("ethereum:"):].lower()
                    token_price_dict[address] = value['price']
            return token_price_dict

    async def _get_price_from_defillama(self, token_addresses, timestamp):
        token_address_groups = [token_addresses[i:i+5] for i in range(0, len(token_addresses), 5)]

        if time.time() - timestamp > 3600 * 6:
            defillama_url = f"https://coins.llama.fi/prices/historical/{timestamp}/"
        else:
            defillama_url = "https://coins.llama.fi/prices/current/"

        async with aiohttp.ClientSession() as session:
            tasks = []
            for group in token_address_groups:
                request_url = defillama_url + ','.join([f"ethereum:{address}" for address in group])
                task = asyncio.create_task(self._fetch_price(session, request_url))
                tasks.append(task)

            results = await asyncio.gather(*tasks)

        token_price_dict = {}
        for result in results:
            token_price_dict.update(result)

        return token_price_dict

    async def _multi_call(self, calls, web3, require_success, block_id):
        multi_call = Multicall(calls, _w3=web3, require_success=require_success, block_id=block_id)
        return multi_call()

    async def _get_eth_balance_for_addresses(self, batch_web3_provider, addresses, block_number):

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