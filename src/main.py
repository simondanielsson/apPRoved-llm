"""Main entry point of the application."""

import asyncio
import logging
import signal

import src.reviews.controllers as reviews_controllers
from src.config import config
from src.reviews.constants import AMQPQueues
from src.utils.amqp import AsyncRabbitMQClient
from src.utils.pubsub import AsyncPubSubSubscriber

logger = logging.getLogger(__name__)


def launch_app() -> None:
    """Launch the application."""
    asyncio.run(listen_for_messages())


async def listen_for_messages() -> None:
    """Listen for messages from the RabbitMQ queue."""
    if config.amqp_mode == "rabbitmq":
        rabbitmq_client = AsyncRabbitMQClient()
        await rabbitmq_client.connect()

        await rabbitmq_client.consume_messages(
            queue_name=AMQPQueues.REVIEW_FILE_DIFF_QUEUE,
            callback=reviews_controllers.create_review_from_file_diffs,
        )
        logger.info("Listening for messages...")
    elif config.amqp_mode == "pubsub":
        logger.info("PubSub mode is not implemented yet")
        project_id = config.gcp_project_id
        subscription_id = config.gcp_subscription_id
        callback = reviews_controllers.create_review_from_file_diffs
        subscriber = AsyncPubSubSubscriber(
            project_id,
            subscription_id,
            callback=callback,
            loop=asyncio.get_running_loop(),
        )

        try:
            await subscriber.start()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        finally:
            await subscriber.stop()
    else:
        logger.error("Invalid AMQP mode, received %s. Exiting...", config.amqp_mode)
        return

    await handle_events()


async def handle_events() -> None:
    """Handle events."""
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def shutdown() -> None:
        logger.info("Received shutdown signal")
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    await stop_event.wait()


if __name__ == "__main__":
    launch_app()
