import logging

from blockchainetl.jobs.exporters.console_item_exporter import ConsoleItemExporter
from blockchainetl.jobs.exporters.in_memory_item_exporter import InMemoryItemExporter
from ethereumetl.domain.trace import EthTrace
from ethereumetl.enumeration.entity_type import EntityType
from ethereumetl.jobs.export_blocks_job import ExportBlocksJob
from ethereumetl.jobs.export_receipts_job import ExportReceiptsJob
from ethereumetl.jobs.export_traces_job import ExportTracesJob
from ethereumetl.jobs.export_geth_traces_job import ExportGethTracesJob
from ethereumetl.jobs.extract_geth_traces_job import ExtractGethTracesJob
from ethereumetl.jobs.extract_contracts_job import ExtractContractsJob
from ethereumetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
from ethereumetl.jobs.extract_tokens_job import ExtractTokensJob
from ethereumetl.service.trace_id_calculator import calculate_trace_ids
from ethereumetl.service.trace_status_calculator import calculate_trace_statuses
from ethereumetl.streaming.enrich import enrich_transactions, enrich_logs, enrich_token_transfers, enrich_traces, \
    enrich_contracts, enrich_tokens, enrich_traces_with_blocks_transactions
from ethereumetl.streaming.eth_item_id_calculator import EthItemIdCalculator
from ethereumetl.streaming.eth_item_timestamp_calculator import EthItemTimestampCalculator
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.web3_utils import build_web3


class EthStreamerAdapter:
    def __init__(
            self,
            batch_web3_provider,
            node_client,
            item_exporter=ConsoleItemExporter(),
            batch_size=100,
            max_workers=5,
            entity_types=tuple(EntityType.ALL_FOR_STREAMING)):
        self.batch_web3_provider = batch_web3_provider
        self.node_client = node_client
        self.item_exporter = item_exporter
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.entity_types = entity_types
        self.item_id_calculator = EthItemIdCalculator()
        self.item_timestamp_calculator = EthItemTimestampCalculator()

    def open(self):
        self.item_exporter.open()

    def get_current_block_number(self):
        w3 = build_web3(self.batch_web3_provider)
        return int(w3.eth.getBlock("latest").number)

    def export_all(self, start_block, end_block):
        # Export blocks and transactions
        blocks, transactions = [], []
        if self._should_export(EntityType.BLOCK) or self._should_export(EntityType.TRANSACTION):
            blocks, transactions = self._export_blocks_and_transactions(start_block, end_block)

        # Export receipts and logs
        receipts, logs = [], []
        if self._should_export(EntityType.RECEIPT) or self._should_export(EntityType.LOG):
            receipts, logs = self._export_receipts_and_logs(transactions)

        # Extract token transfers
        token_transfers = []
        if self._should_export(EntityType.TOKEN_TRANSFER):
            token_transfers = self._extract_token_transfers(logs)

        # Export traces
        traces = []
        if self._should_export(EntityType.TRACE):
            # use node client to check which client to get trace
            # 直接在这里补trace status,index 等字段不行，这里raw_traces没有trx_hash只有enrich 之后才能继续提取
            traces = self._export_traces(start_block, end_block, self.node_client)

        # Export contracts
        contracts = []
        if self._should_export(EntityType.CONTRACT):
            contracts = self._export_contracts(traces)

        # Export tokens
        tokens = []
        if self._should_export(EntityType.TOKEN):
            tokens = self._extract_tokens(contracts)

        enriched_blocks = blocks \
            if EntityType.BLOCK in self.entity_types else []
        enriched_transactions = enrich_transactions(transactions, receipts) \
            if EntityType.TRANSACTION in self.entity_types else []
        enriched_logs = enrich_logs(blocks, logs) \
            if EntityType.LOG in self.entity_types else []
        enriched_token_transfers = enrich_token_transfers(blocks, token_transfers) \
            if EntityType.TOKEN_TRANSFER in self.entity_types else []
        enriched_traces = enrich_traces(blocks, traces) \
            if EntityType.TRACE in self.entity_types else []
        enriched_contracts = enrich_contracts(blocks, contracts) \
            if EntityType.CONTRACT in self.entity_types else []
        enriched_tokens = enrich_tokens(blocks, tokens) \
            if EntityType.TOKEN in self.entity_types else []
        
        # enrich trace 
        if self.node_client == "geth":
            # 1) firsh enrich to get transactions_hash
            enriched_traces_by_blocks_transactions = enrich_traces_with_blocks_transactions(blocks, traces, transactions)
            # 2) 补充trace_status
            # dict -> trace object
            trs = []
            for tr in enriched_traces_by_blocks_transactions:
                trs.append(dict_to_eth_trace(tr))
            calculate_trace_statuses(trs)
            calculate_trace_ids(trs)
            # calculate trace index
            for ind, trace in enumerate(trs):
                trace.trace_index = ind
                enriched_traces[ind] = eth_trace_to_dict(trace)
        logging.info('Exporting with ' + type(self.item_exporter).__name__)

        all_items = \
            sort_by(enriched_blocks, 'number') + \
            sort_by(enriched_transactions, ('block_number', 'transaction_index')) + \
            sort_by(enriched_logs, ('block_number', 'log_index')) + \
            sort_by(enriched_token_transfers, ('block_number', 'log_index')) + \
            sort_by(enriched_traces, ('block_number', 'trace_index')) + \
            sort_by(enriched_contracts, ('block_number',)) + \
            sort_by(enriched_tokens, ('block_number',))

        self.calculate_item_ids(all_items)
        self.calculate_item_timestamps(all_items)

        self.item_exporter.export_items(all_items)

    def _export_blocks_and_transactions(self, start_block, end_block):
        blocks_and_transactions_item_exporter = InMemoryItemExporter(item_types=['block', 'transaction'])
        blocks_and_transactions_job = ExportBlocksJob(
            start_block=start_block,
            end_block=end_block,
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=blocks_and_transactions_item_exporter,
            export_blocks=self._should_export(EntityType.BLOCK),
            export_transactions=self._should_export(EntityType.TRANSACTION)
        )
        blocks_and_transactions_job.run()
        blocks = blocks_and_transactions_item_exporter.get_items('block')
        transactions = blocks_and_transactions_item_exporter.get_items('transaction')
        return blocks, transactions

    def _export_receipts_and_logs(self, transactions):
        exporter = InMemoryItemExporter(item_types=['receipt', 'log'])
        job = ExportReceiptsJob(
            transaction_hashes_iterable=(transaction['hash'] for transaction in transactions),
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=exporter,
            export_receipts=self._should_export(EntityType.RECEIPT),
            export_logs=self._should_export(EntityType.LOG)
        )
        job.run()
        receipts = exporter.get_items('receipt')
        logs = exporter.get_items('log')
        return receipts, logs

    def _extract_token_transfers(self, logs):
        exporter = InMemoryItemExporter(item_types=['token_transfer'])
        job = ExtractTokenTransfersJob(
            logs_iterable=logs,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=exporter)
        job.run()
        token_transfers = exporter.get_items('token_transfer')
        return token_transfers

    def _export_traces(self, start_block, end_block, node_client):
        exporter = InMemoryItemExporter(item_types=['trace'])
        if node_client == "geth":
            job = ExportGethTracesJob(
                start_block=start_block,
                end_block=end_block,
                batch_size=self.batch_size,
                batch_web3_provider=self.batch_web3_provider,
                max_workers=self.max_workers,
                item_exporter=exporter
            )
        else:
            job = ExportTracesJob(
                start_block=start_block,
                end_block=end_block,
                batch_size=self.batch_size,
                web3=ThreadLocalProxy(lambda: build_web3(self.batch_web3_provider)),
                max_workers=self.max_workers,
                item_exporter=exporter
            )

        job.run()
        traces = exporter.get_items('trace')
        return traces

    def _export_contracts(self, traces):
        exporter = InMemoryItemExporter(item_types=['contract'])
        job = ExtractContractsJob(
            traces_iterable=traces,
            batch_size=self.batch_size,
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        contracts = exporter.get_items('contract')
        return contracts

    def _extract_tokens(self, contracts):
        exporter = InMemoryItemExporter(item_types=['token'])
        job = ExtractTokensJob(
            contracts_iterable=contracts,
            web3=ThreadLocalProxy(lambda: build_web3(self.batch_web3_provider)),
            max_workers=self.max_workers,
            item_exporter=exporter
        )
        job.run()
        tokens = exporter.get_items('token')
        return tokens

    def _should_export(self, entity_type):
        if entity_type == EntityType.BLOCK:
            return True

        if entity_type == EntityType.TRANSACTION:
            return EntityType.TRANSACTION in self.entity_types or self._should_export(EntityType.LOG)

        if entity_type == EntityType.RECEIPT:
            return EntityType.TRANSACTION in self.entity_types or self._should_export(EntityType.TOKEN_TRANSFER)

        if entity_type == EntityType.LOG:
            return EntityType.LOG in self.entity_types or self._should_export(EntityType.TOKEN_TRANSFER)

        if entity_type == EntityType.TOKEN_TRANSFER:
            return EntityType.TOKEN_TRANSFER in self.entity_types

        if entity_type == EntityType.TRACE:
            return EntityType.TRACE in self.entity_types or self._should_export(EntityType.CONTRACT)

        if entity_type == EntityType.CONTRACT:
            return EntityType.CONTRACT in self.entity_types or self._should_export(EntityType.TOKEN)

        if entity_type == EntityType.TOKEN:
            return EntityType.TOKEN in self.entity_types

        raise ValueError('Unexpected entity type ' + entity_type)

    def calculate_item_ids(self, items):
        for item in items:
            item['item_id'] = self.item_id_calculator.calculate(item)

    def calculate_item_timestamps(self, items):
        for item in items:
            item['item_timestamp'] = self.item_timestamp_calculator.calculate(item)

    def close(self):
        self.item_exporter.close()


def sort_by(arr, fields):
    if isinstance(fields, tuple):
        fields = tuple(fields)
    return sorted(arr, key=lambda item: tuple(item.get(f) for f in fields))


def dict_to_eth_trace(json_dict):
    trace = EthTrace()
    trace.transaction_hash = json_dict['transaction_hash'] if 'transaction_hash' in json_dict else None
    trace.transaction_index = json_dict['transaction_index'] if 'transaction_index' in json_dict else None
    trace.from_address = json_dict['from_address'] if 'from_address' in json_dict else None
    trace.to_address = json_dict['to_address'] if 'to_address' in json_dict else None
    trace.value = json_dict['value'] if 'value' in json_dict else None
    trace.input = json_dict['input'] if 'input' in json_dict else None
    trace.output = json_dict['output'] if 'output' in json_dict else None
    trace.trace_type = json_dict['trace_type'] if 'trace_type' in json_dict else None
    trace.gas = json_dict['gas'] if 'gas' in json_dict else None
    trace.gas_used = json_dict['gas_used'] if 'gas_used' in json_dict else None
    trace.subtraces = json_dict['subtraces'] if 'subtraces' in json_dict else None
    trace.trace_address = json_dict['trace_address'] if 'trace_address' in json_dict else None
    trace.error = json_dict['error'] if 'error' in json_dict else None
    trace.status = json_dict['status'] if 'status' in json_dict else None
    trace.block_number = json_dict['block_number'] if 'block_number' in json_dict else None
    trace.trace_id = json_dict['trace_id'] if 'trace_id' in json_dict else None
    trace.trace_index = json_dict['trace_index'] if 'trace_index' in json_dict else None
    return trace


def eth_trace_to_dict(eth_trace):
    json_dict = {
        'transaction_hash': eth_trace.transaction_hash,
        'transaction_index': eth_trace.transaction_index,
        'from_address': eth_trace.from_address,
        'to_address': eth_trace.to_address,
        'value': eth_trace.value,
        'input': eth_trace.input,
        'output': eth_trace.output,
        'trace_type': eth_trace.trace_type,
        'gas': eth_trace.gas,
        'gas_used': eth_trace.gas_used,
        'subtraces': eth_trace.subtraces,
        'trace_address': eth_trace.trace_address,
        'error': eth_trace.error,
        'status': eth_trace.status,
        'block_number': eth_trace.block_number,
        'trace_id': eth_trace.trace_id,
        'trace_index': eth_trace.trace_index
    }
    return json_dict