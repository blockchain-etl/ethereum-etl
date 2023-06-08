import collections
import logging
from datetime import datetime

from sqlalchemy import create_engine

from blockchainetl.jobs.exporters.converters.composite_item_converter import \
  CompositeItemConverter


class MySQLItemExporter:
  logger = logging.getLogger('MySQLItemExporter')

  def __init__(
      self, connection_url, item_type_to_insert_stmt_mapping,
      converters=(), print_sql=False
  ):
    self.connection_url = connection_url
    self.item_type_to_insert_stmt_mapping = item_type_to_insert_stmt_mapping
    self.converter = CompositeItemConverter(converters)
    self.print_sql = print_sql

    self.engine = self.create_engine()

  def open(self):
    pass

  def export_items(self, items):
    start_time = datetime.now()
    items_grouped_by_type = group_by_item_type(items)

    for item_type, insert_stmt in self.item_type_to_insert_stmt_mapping.items():
      item_group = items_grouped_by_type.get(item_type)
      if item_group:
        connection = self.engine.connect()
        converted_items = list(self.convert_items(item_group))
        connection.execute(insert_stmt, converted_items)
        connection.commit()
    duration = datetime.now() - start_time
    self.logger.info(
        f"Finished write. Total items processed: {len(items)}. Took {str(duration)}."
    )

  def convert_items(self, items):
    for item in items:
      yield self.converter.convert_item(item)

  def create_engine(self):
    engine = create_engine(self.connection_url, echo=self.print_sql,
                           pool_recycle=3600)
    return engine

  def close(self):
    pass


def group_by_item_type(items):
  result = collections.defaultdict(list)
  for item in items:
    result[item.get('type')].append(item)

  return result
