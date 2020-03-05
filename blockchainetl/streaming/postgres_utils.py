from sqlalchemy.dialects.postgresql import insert


def create_insert_statement_for_table(table):
    insert_stmt = insert(table)

    insert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[column.name for column in table.columns if column.primary_key],
        set_={
            column.name: insert_stmt.excluded[column.name] for column in table.columns if not column.primary_key
        }
    )

    return insert_stmt
