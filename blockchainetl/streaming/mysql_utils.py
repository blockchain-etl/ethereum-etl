from sqlalchemy.dialects.mysql import insert


def create_insert_statement_for_table(table):
    insert_stmt = insert(table)

    return insert_stmt
