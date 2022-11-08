import json
import logging
import pika
import pika.exceptions


class RabbitMQItemExporter:
    OUTPUT_FORMAT_ERROR = 'Invalid rabbitmq output param. It should be in format of ' \
                          '"rabbitmq/{username}:{password}@localhost:5672/{queue-name}"'
    CONNECTION_ERROR = "Invalid output values or broker not running."

    def __init__(self, output):
        self.connection_url = self._get_connection_url(output)
        self.queue_name = self._get_queue_name(output)
        self._connection = None
        self._channel = None
        self.connect()

    def open(self):
        pass

    def connect(self):
        if not self._connection or self._connection.is_closed:
            try:
                self._connection = pika.BlockingConnection(pika.URLParameters(self.connection_url))
            except pika.exceptions.AMQPConnectionError:
                raise Exception(self.CONNECTION_ERROR)
            self._channel = self._connection.channel()
            self._channel.queue_declare(queue=self.queue_name, durable=True)
            self._channel.confirm_delivery()

    def _get_connection_url(self, output):
        try:
            return f"amqp://{output.split('/')[1]}"
        except (KeyError, IndexError):
            raise Exception(self.OUTPUT_FORMAT_ERROR)

    def _get_queue_name(self, output):
        try:
            return output.split('/')[-1]
        except (KeyError, IndexError):
            raise Exception(self.OUTPUT_FORMAT_ERROR)

    def _publish(self, msg):
        self._channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(msg).encode(),
            properties=pika.BasicProperties(
                content_type='application/json',
                delivery_mode=pika.DeliveryMode.Persistent)
        )
        logging.debug('message sent: %s', msg)

    def publish(self, msg):
        """Publish msg, reconnecting if necessary."""

        try:
            self._publish(msg)
        except (
                pika.exceptions.ConnectionClosed,
                pika.exceptions.ChannelWrongStateError,
                pika.exceptions.StreamLostError
        ):
            logging.debug('reconnecting to queue')
            self.connect()
            self._publish(msg)

    def export_items(self, items):
        for item in items:
            self.publish(item)

    def close(self):
        pass
