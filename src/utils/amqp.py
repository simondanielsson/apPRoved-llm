import logging
import asyncio
import json
import multiprocessing
from typing import Awaitable, Callable, Any

import aio_pika

from src.config import config

logger = logging.getLogger(__name__)


class AsyncRabbitMQClient:
    def __init__(self):
        self._amqp_url = config.amqp_url
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.RobustChannel | None = None

    async def connect(self):
        """Establishes an asynchronous connection to RabbitMQ."""
        self._connection = await aio_pika.connect_robust(self._amqp_url)
        self._channel = await self._connection.channel()

    async def close(self):
        """Closes the RabbitMQ connection."""
        if self._channel is not None:
            await self._channel.close()

        if self._connection is not None:
            await self._connection.close()

    async def publish_message(self, queue_name: str, message: str):
        """
        Publishes a message to a specified queue.

        :param queue_name: The name of the queue.
        :param message: The message to be published.
        """
        queue = await self._channel.declare_queue(queue_name, durable=True)
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()), routing_key=queue.name
        )

    async def consume_messages(
        self,
        queue_name: str,
        callback: Callable[[dict], Awaitable[None]],
        run_in_process: bool = False,
        **kwargs,
    ):
        """
        Starts consuming messages from a specified queue with an asynchronous callback function.

        :param queue_name: The name of the queue.
        :param callback: The asynchronous callback function to process messages. Should be wrapped
            in in `process_callback` if the callback is CPU-bound.
        """
        if self._channel is None:
            raise ValueError(
                "RabbitMQ connection has not been established. Run `connect` first."
            )

        queue = await self._channel.declare_queue(queue_name, durable=True)
        if run_in_process:

            async def target(message: aio_pika.IncomingMessage):
                self.wrap_message_handler_for_process(
                    process_target=callback,
                    semaphore=kwargs.get("semaphore", multiprocessing.Semaphore(10)),
                    message=message,
                )

        else:
            target = self.wrap_message_handler(callback)

        await queue.consume(target)

    @staticmethod
    def wrap_message_handler(
        callback: Callable[[dict], Awaitable[None]],
    ) -> Callable[[aio_pika.IncomingMessage], Awaitable[None]]:
        """Prints the message body."""

        async def process_message(message: aio_pika.IncomingMessage):
            try:
                async with message.process():
                    message_json = json.loads(message.body)
                    await callback(message_json)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await message.reject(requeue=False)

        return process_message

    @staticmethod
    def wrap_message_handler_for_process(
        message: aio_pika.IncomingMessage,
        process_target: Callable[[dict], Awaitable[None]],
        semaphore: multiprocessing.Semaphore,
    ):
        """Runs the callback function in a separate process.

        :param message: The incoming message.
        :param process_target: The target function to process the message.
        :param semaphore: The semaphore to control the number of concurrent processes.
        """

        async def process_message():
            async with message.process():
                message_json = json.loads(message.body)

            # Acquire the semaphore before starting the new process
            semaphore.acquire()

            process = multiprocessing.Process(
                target=async_worker,
                args=(process_target, message_json, semaphore),
            )
            process.start()

        asyncio.create_task(process_message())


def async_worker(
    process_target: Callable[[dict], Any],
    message: dict,
    semaphore: multiprocessing.Semaphore,
):
    try:
        asyncio.run(process_target(message))
    except Exception as e:
        print(e)
        raise
    finally:
        semaphore.release()