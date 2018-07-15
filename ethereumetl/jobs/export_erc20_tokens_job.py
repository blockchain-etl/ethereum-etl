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
from ethereumetl.mappers.erc20_token_mapper import EthErc20TokenMapper
from ethereumetl.service.erc20_token_service import EthErc20TokenService


class ExportErc20TokensJob(BaseJob):
    def __init__(self, web3, item_exporter, token_addresses_iterable, max_workers):
        self.item_exporter = item_exporter
        self.token_addresses_iterable = token_addresses_iterable
        self.batch_work_executor = BatchWorkExecutor(1, max_workers)

        self.erc20_token_service = EthErc20TokenService(web3, clean_user_provided_content)
        self.erc20_token_mapper = EthErc20TokenMapper()

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(self.token_addresses_iterable, self._export_tokens)

    def _export_tokens(self, token_addresses):
        for token_address in token_addresses:
            self._export_token(token_address)

    def _export_token(self, token_address):
        token = self.erc20_token_service.get_token(token_address)
        token_dict = self.erc20_token_mapper.erc20_token_to_dict(token)
        self.item_exporter.export_item(token_dict)

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()


# https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#numeric-type
BIG_QUERY_NUMERIC_MAX_VALUE = 99999999999999999999999999999
ASCII_0 = 0


def clean_user_provided_content(content):
    if isinstance(content, str):
        # This prevents this error in BigQuery
        # Error while reading data, error message: Error detected while parsing row starting at position: 9999.
        # Error: Bad character (ASCII 0) encountered.
        return content.translate({ASCII_0: None})
    elif isinstance(content, int):
        # NUMERIC type in BigQuery is 16 bytes
        # https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types#numeric-type
        return content if content <= BIG_QUERY_NUMERIC_MAX_VALUE else None
    else:
        return content
