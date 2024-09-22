"""Utility functions for making API requests."""

import logging

from src.config import config
from src.reviews.constants import ReviewStatus
from src.reviews.dto.requests import CompleteReviewRequest, UpdateProgressRequest
from src.reviews.models.pull_requests import FileReview
from src.utils.http import send_http_post_request, send_http_put_request

logger = logging.getLogger(__name__)


async def update_progress(
    review_status_id: int,
    progress: int,
    status: ReviewStatus,
) -> None:
    """Update progress of a review."""
    payload = UpdateProgressRequest(
        progress=progress,
        status=status,
    )

    url = f"{config.approved_api_url}/review-status/{review_status_id}"
    logger.info(
        "Updating progress of review status %s to %s",
        review_status_id,
        progress,
    )
    await send_http_put_request(content=payload.model_dump(), url=url)


async def complete_review(
    review_id: int,
    review_status_id: int,
    file_reviews: list[FileReview],
) -> None:
    """Complete a review."""
    review = CompleteReviewRequest(
        review_id=review_id,
        review_status_id=review_status_id,
        file_reviews=file_reviews,
    )
    url = f"{config.approved_api_url}/reviews/complete"
    logger.info("Completing review %s", review_id)
    await send_http_post_request(content=review.model_dump(), url=url)
