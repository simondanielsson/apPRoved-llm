"""Constants for the reviews module."""

from enum import StrEnum, auto


class AMQPQueues(StrEnum):
    """Constants for the AMQP queues used by the reviews module."""

    REVIEW_FILE_DIFF_QUEUE = "review-file-diffs"


class ReviewStatus(StrEnum):
    """Constants for the review status."""

    queued = auto()
    processing = auto()
    available = auto()
