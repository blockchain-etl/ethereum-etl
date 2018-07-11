from ethereumetl.jobs.composite_item_exporter import CompositeItemExporter

FIELDS_TO_EXPORT = [
    'erc20_token_address',
    'erc20_token_symbol',
    'erc20_token_name',
    'erc20_token_decimals',
    'erc20_token_total_supply'
]


def export_erc20_tokens_job_item_exporter(erc20_tokens_output):
    return CompositeItemExporter(
        filename_mapping={
            'erc20_token': erc20_tokens_output
        },
        field_mapping={
            'erc20_token': FIELDS_TO_EXPORT
        }
    )
