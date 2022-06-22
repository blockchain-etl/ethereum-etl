import logging
import signal
import sys

from blockchainetl.jobs.exporters.console_item_exporter import ConsoleItemExporter
from blockchainetl.logging_utils import logging_basic_config


def get_item_exporter(output,
                      topic_prefix
                      ):
    item_type_to_topic_mapping = {
        "block": topic_prefix + ".blocks",
        "transaction": topic_prefix + ".transactions",
        "log": topic_prefix + ".logs",
        "token_transfer": topic_prefix + ".token_transfers",
        "trace": topic_prefix + ".traces",
        "contract": topic_prefix + ".contracts",
        "token": topic_prefix + ".tokens",
    }

    if output == "gcp":
        from blockchainetl.jobs.exporters.google_pubsub_item_exporter import GooglePubSubItemExporter
        item_exporter = GooglePubSubItemExporter(item_type_to_topic_mapping)

    elif output == "kafka":
        from blockchainetl.jobs.exporters.kafka_item_exporter import KafkaItemExporter
        item_exporter = KafkaItemExporter(item_type_to_topic_mapping)

    else:
        item_exporter = ConsoleItemExporter()

    return item_exporter


def configure_signals():
    def sigterm_handler(_signo, _stack_frame):
        # Raises SystemExit(0):
        sys.exit(0)

    signal.signal(signal.SIGTERM, sigterm_handler)


def configure_logging(filename):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging_basic_config(filename=filename)
