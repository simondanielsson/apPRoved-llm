"""Module containing message queue subscribers."""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Self

from google.api_core.exceptions import GoogleAPICallError, RetryError
from google.cloud import pubsub_v1

logger = logging.getLogger(__name__)


class MessageQueueSubscriber(ABC):
    """MessageQueueSubscriber is an abstract class for message queue subscribers."""

    @abstractmethod
    async def start(self: Self) -> None:
        """Start the subscriber."""
        raise NotImplementedError

    @abstractmethod
    async def stop(self: Self) -> None:
        """Stop the subscriber."""
        raise NotImplementedError


class AsyncPubSubSubscriber(MessageQueueSubscriber):
    """AsyncPubSubSubscriber is a message queue subscriber that listens for messages."""

    def __init__(
        self: Self,
        project_id: str,
        subscription_id: str,
        callback: Callable[[Any], Awaitable[None]],
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        """Initialize the subscriber."""
        self.project_id = project_id
        self.subscription_id = subscription_id
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project_id,
            subscription_id,
        )
        self.running = False
        self.callback = callback
        self.loop = loop
        self.semaphore = asyncio.Semaphore(4)

    async def start(self: Self) -> None:
        """Start the subscriber to pull messages asynchronously."""
        self.running = True

        def message_callback(message: pubsub_v1.subscriber.message.Message) -> None:
            # The callback is synchronous, so we need to run the async handler
            asyncio.run_coroutine_threadsafe(
                self._handle_message(message),
                self.loop,
            )

        try:
            logger.info("Listening for messages on %s...", self.subscription_path)
            self.subscriber.subscribe(self.subscription_path, callback=message_callback)

            while self.running:
                await asyncio.sleep(5)

        except (GoogleAPICallError, RetryError) as e:
            logger.info("Error handling message: %s", e)

        finally:
            await self.stop()

    async def _handle_message(
        self: Self,
        message: pubsub_v1.subscriber.message.Message,
    ) -> None:
        """Process each message asynchronously."""
        async with self.semaphore:
            try:
                message_data = message.data.decode("utf-8")
                logger.info("Received message")
                message_dict = json.loads(message_data)
                await self.callback(message_dict)
                message.ack()
            except Exception:
                logger.info("Error handling message, nacking...")
                message.nack()

    async def stop(self: Self) -> None:
        """Stop the subscriber gracefully."""
        logger.info("Stopping subscriber...")
        self.running = False
        self.subscriber.close()
