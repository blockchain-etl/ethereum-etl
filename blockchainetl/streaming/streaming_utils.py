import logging
import signal
import sys

from blockchainetl.jobs.exporters.console_item_exporter import ConsoleItemExporter
from blockchainetl.logging_utils import logging_basic_config


def get_item_exporter(output, lag=0):
    if output == "gcp":
        from blockchainetl.jobs.exporters.google_pubsub_item_exporter import (
            GooglePubSubItemExporter,
        )

        item_exporter = GooglePubSubItemExporter(
            item_type_to_topic_mapping={
                "block": output + ".blocks",
                "transaction": output + ".transactions",
                "log": output + ".logs",
                "token_transfer": output + ".token_transfers",
                "trace": output + ".traces",
                "contract": output + ".contracts",
                "token": output + ".tokens",
            }
        )
    elif output == "kafka":
        from blockchainetl.jobs.exporters.kafka_item_exporter import KafkaItemExporter

        prefix = "eth"
        suffix = "hot"
        if lag > 0:
            suffix = "warm"
        item_exporter = KafkaItemExporter(
            item_type_to_topic_mapping={
                "block": prefix + "-blocks-" + suffix,
                "transaction": prefix + "-transactions-" + suffix,
                "log": prefix + "-logs-" + suffix,
                "token_transfer": prefix + "-token-transfers-" + suffix,
                "trace": prefix + "-traces-" + suffix,
                "contract": prefix + "-contracts-" + suffix,
                "token": prefix + "-tokens-" + suffix,
            }
        )
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
