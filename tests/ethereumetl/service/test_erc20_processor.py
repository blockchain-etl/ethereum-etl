from ethereumetl.domain.transaction_receipt_log import EthTransactionReceiptLog
from ethereumetl.service.erc20_processor import EthErc20Processor

# https://ethereum.stackexchange.com/questions/12553/understanding-logs-and-log-blooms
TRANSFER_EVENT_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

erc20_processor = EthErc20Processor()


def test_filter_transfer_from_receipt_log():
    log = EthTransactionReceiptLog()
    log.address = '0x25c6413359059694A7FCa8e599Ae39Ce1C944Da2'
    log.block_number = 1061946
    log.data = '0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc18'
    log.log_index = 0
    log.topics = ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
                  '0x000000000000000000000000e9eeaec75883f0e389a78e2260bfac1776df2f1d',
                  '0x0000000000000000000000000000000000000000000000000000000000000000']
    log.transaction_hash = '0xd62a74c7b04e8e0539398f6ba6a5eb11ad8aa862e77f0af718f0fad19b0b0480'
    erc20_transfer = erc20_processor.filter_transfer_from_receipt_log(log)

    assert erc20_transfer.erc20_token == '0x25c6413359059694A7FCa8e599Ae39Ce1C944Da2'
    assert erc20_transfer.erc20_from == '0x000000000000000000000000e9eeaec75883f0e389a78e2260bfac1776df2f1d'
    assert erc20_transfer.erc20_to == '0x0000000000000000000000000000000000000000000000000000000000000000'
    assert erc20_transfer.erc20_tx_hash == '0xd62a74c7b04e8e0539398f6ba6a5eb11ad8aa862e77f0af718f0fad19b0b0480'
    assert erc20_transfer.erc20_block_number == 1061946
    assert erc20_transfer.erc20_value == 115792089237316195423570985008687907853269984665640564039457584007913129638936
