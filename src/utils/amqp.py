"""AMQP client for RabbitMQ."""

import asyncio
import json
import logging
import multiprocessing
from multiprocessing.synchronize import Semaphore
from typing import Any, Callable, Coroutine, Self

import aio_pika

from src.config import config

logger = logging.getLogger(__name__)

DictCoroutineType = Callable[[dict], Coroutine[Any, Any, None]]
MessageCoroutineType = Callable[[aio_pika.IncomingMessage], Coroutine[Any, Any, None]]


class AsyncRabbitMQClient:
    """Asynchronous RabbitMQ client."""

    def __init__(self: Self) -> None:
        """Initialize the RabbitMQ client."""
        self._amqp_url = config.amqp_url
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.RobustChannel | None = None

    async def connect(self: Self) -> None:
        """Establish an asynchronous connection to RabbitMQ."""
        self._connection = await aio_pika.connect_robust(self._amqp_url)
        self._channel = await self._connection.channel()

    async def close(self: Self) -> None:
        """Close the RabbitMQ connection."""
        if self._channel is not None:
            await self._channel.close()

        if self._connection is not None:
            await self._connection.close()

    async def publish_message(self: Self, queue_name: str, message: str) -> None:
        """Publish a message to a specified queue.

        :param queue_name: The name of the queue.
        :param message: The message to be published.
        """
        if self._channel is None:
            message = (
                "RabbitMQ connection has not been established. Run `connect` first."
            )
            raise ValueError(message)

        queue = await self._channel.declare_queue(queue_name, durable=True)
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=queue.name,
        )

    async def consume_messages(
        self: Self,
        queue_name: str,
        callback: DictCoroutineType,
        *,
        run_in_process: bool = False,
        **kwargs: Any,
    ) -> None:
        """Consume messages from queue with callback function.

        :param queue_name: The name of the queue.
        :param callback: The asynchronous callback function to process messages.
            Should be wrapped in in `process_callback` if the callback is CPU-bound.
        """
        if self._channel is None:
            msg = "RabbitMQ connection has not been established. Run `connect` first."
            raise ValueError(
                msg,
            )

        queue = await self._channel.declare_queue(queue_name, durable=True)

        target: MessageCoroutineType = (
            self.wrap_message_handler_for_process(
                callback,
                kwargs.get("semaphore"),
            )
            if run_in_process
            else self.wrap_message_handler(callback)
        )

        await queue.consume(target)

    @staticmethod
    def wrap_message_handler(
        callback: DictCoroutineType,
    ) -> MessageCoroutineType:
        """Wrap the callback function to process the incoming message."""

        async def process_message(message: aio_pika.IncomingMessage) -> None:
            try:
                async with message.process():
                    message_json = json.loads(message.body)
                    await callback(message_json)
            except Exception:
                logger.exception("Error processing message")
                await message.reject(requeue=False)

        return process_message

    @staticmethod
    def wrap_message_handler_for_process(
        callback: DictCoroutineType,
        semaphore: Semaphore | None = None,
    ) -> MessageCoroutineType:
        """Wrap and run the callback function in a separate process.

        :param message: The incoming message.
        :param process_target: The target function to process the message.
        :param semaphore: The semaphore to control the number of concurrent processes.
        """
        semaphore = semaphore or multiprocessing.Semaphore(10)

        async def run_in_process(message: aio_pika.IncomingMessage) -> None:
            async def process_message() -> None:
                async with message.process():
                    message_json = json.loads(message.body)

                # Acquire the semaphore before starting the new process
                semaphore.acquire()

                process = multiprocessing.Process(
                    target=async_worker,
                    args=(callback, message_json, semaphore),
                )
                process.start()

            _ = asyncio.create_task(process_message())

        return run_in_process


def async_worker(
    process_target: DictCoroutineType,
    message: dict,
    semaphore: Semaphore,
) -> None:
    """Run the target function asynchronously in a separate process."""
    try:
        asyncio.run(process_target(message))
    except Exception as e:
        logger.warning(e)
        raise
    finally:
        semaphore.release()
