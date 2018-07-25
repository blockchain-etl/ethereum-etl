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

from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from ethereumetl.jobs.base_job import BaseJob
from ethereumetl.mappers.erc20_transfer_mapper import EthErc20TransferMapper
from ethereumetl.mappers.receipt_log_mapper import EthReceiptLogMapper
from ethereumetl.service.erc20_transfer_extractor import EthErc20TransferExtractor


class ExtractErc20TransfersJob(BaseJob):
    def __init__(
            self,
            logs_iterable,
            batch_size,
            max_workers,
            item_exporter):
        self.logs_iterable = logs_iterable

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.receipt_log_mapper = EthReceiptLogMapper()
        self.erc20_transfer_mapper = EthErc20TransferMapper()
        self.erc20_transfer_extractor = EthErc20TransferExtractor()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(self.logs_iterable, self._extract_transfers)

    def _extract_transfers(self, log_dicts):
        for log_dict in log_dicts:
            self._extract_transfer(log_dict)

    def _extract_transfer(self, log_dict):
        log = self.receipt_log_mapper.dict_to_receipt_log(log_dict)
        erc20_transfer = self.erc20_transfer_extractor.extract_transfer_from_log(log)
        if erc20_transfer is not None:
            self.item_exporter.export_item(self.erc20_transfer_mapper.erc20_transfer_to_dict(erc20_transfer))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
