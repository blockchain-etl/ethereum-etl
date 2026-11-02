from unittest.mock import Mock

import pytest

from ethereumetl.streaming.eth_streamer_adapter import EthStreamerAdapter, sort_by


@pytest.mark.parametrize("items, fields, expected", [
    ([{"number": 102}, {"number": 100}, {"number": 101}], "number", [100, 101, 102]),
    ([{"number": 102}, {"number": 100}, {"number": 101}], ("number",), [100, 101, 102]),
    ([], "number", []),
])
def test_sort_by_block_number(items, fields, expected):
    original = list(items)
    assert [item["number"] for item in sort_by(items, fields)] == expected
    assert items == original


def test_sort_by_multiple_fields():
    items = [
        {"block_number": 2, "transaction_index": 0},
        {"block_number": 1, "transaction_index": 1},
        {"block_number": 1, "transaction_index": 0},
    ]
    assert sort_by(items, ("block_number", "transaction_index")) == [items[2], items[1], items[0]]


def test_stream_exports_blocks_in_number_order(monkeypatch):
    exporter = Mock()
    adapter = EthStreamerAdapter(None, item_exporter=exporter, entity_types=["block"])
    blocks = [{"type": "block", "number": n, "hash": "0x" + str(n), "timestamp": 1600000000 + n}
              for n in [102, 100, 101]]
    monkeypatch.setattr(adapter, "_export_blocks_and_transactions", lambda start, end: (blocks, []))

    adapter.export_all(100, 102)

    exported = exporter.export_items.call_args[0][0]
    assert [item["number"] for item in exported] == [100, 101, 102]
    assert all(item["item_id"] and item["item_timestamp"] for item in exported)
