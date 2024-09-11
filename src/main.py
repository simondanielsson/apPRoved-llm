import asyncio
import signal
import logging

from src.reviews.constants import AMQPQueues
import src.reviews.controllers as reviews_controllers
from src.utils.amqp import AsyncRabbitMQClient

logger = logging.getLogger(__name__)


async def main():
    """Listen for messages from the RabbitMQ queue."""
    rabbitmq_client = AsyncRabbitMQClient()
    await rabbitmq_client.connect()

    await rabbitmq_client.consume_messages(
        queue_name=AMQPQueues.REVIEW_FILE_DIFF_QUEUE,
        callback=reviews_controllers.create_review_from_file_diffs,
    )
    logger.info("Listening for messages...")

    await handle_events()


async def handle_events():
    """Handle events."""
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def shutdown():
        logger.info("Received shutdown signal")
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    await stop_event.wait()


if __name__ == "__main__":
    # This is the entry point of the application.
    from src.config import config

    asyncio.run(main())