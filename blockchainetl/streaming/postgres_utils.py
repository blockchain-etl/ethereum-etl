from sqlalchemy.dialects.postgresql import insert


def create_insert_statement_for_table(table):
    insert_stmt = insert(table)

    primary_key_fields = [column.name for column in table.columns if column.primary_key]
    if primary_key_fields:
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=primary_key_fields,
            set_={
                column.name: insert_stmt.excluded[column.name] for column in table.columns if not column.primary_key
            }
        )

    return insert_stmt
