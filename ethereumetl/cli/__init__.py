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
import click

from ethereumetl.cli import export_blocks_and_transactions, export_receipts_and_logs, export_all, \
    export_token_transfers, extract_token_transfers, export_contracts, export_tokens, get_block_range_for_date, \
    get_block_range_for_timestamps, get_keccak_hash, export_traces


@click.group()
@click.pass_context
def cli(ctx):
    pass


# export
cli.add_command(export_all.cli, "export_all")
cli.add_command(export_blocks_and_transactions.cli, "export_blocks_and_transactions")
cli.add_command(export_receipts_and_logs.cli, "export_receipts_and_logs")
cli.add_command(export_token_transfers.cli, "export_token_transfers")
cli.add_command(extract_token_transfers.cli, "extract_token_transfers")
cli.add_command(export_contracts.cli, "export_contracts")
cli.add_command(export_tokens.cli, "export_tokens")
cli.add_command(export_traces.cli, "export_traces")
# cli.add_command(export_geth_traces.cli, "export_geth_traces")
# cli.add_command(extract_geth_traces.cli, "extract_geth_traces")

# utils
cli.add_command(get_block_range_for_date.cli, "get_block_range_for_date")
cli.add_command(get_block_range_for_timestamps.cli, "get_block_range_for_timestamps")
cli.add_command(get_keccak_hash.cli, "get_keccak_hash")

