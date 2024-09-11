"""Constants for the reviews module."""

from enum import StrEnum


class AMQPQueues(StrEnum):
    """Constants for the AMQP queues used by the reviews module."""

    REVIEW_FILE_DIFF_QUEUE = "review-file-diffs"
