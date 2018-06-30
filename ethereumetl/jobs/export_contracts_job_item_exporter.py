from ethereumetl.jobs.composite_item_exporter import CompositeItemExporter

FIELDS_TO_EXPORT = [
    'contract_address',
    'contract_bytecode'
]


def export_contracts_job_item_exporter(contracts_output):
    return CompositeItemExporter(
        filename_mapping={
            'contract': contracts_output
        },
        field_mapping={
            'contract': FIELDS_TO_EXPORT
        }
    )
