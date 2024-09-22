"""Module for pull request services."""

import asyncio
import logging

from src.common.tools.review_pull_request import ReviewPullRequest
from src.config import config
from src.reviews.constants import ReviewStatus
from src.reviews.models.pull_requests import FileReview, PullRequestFileChanges
from src.utils import api

logger = logging.getLogger(__name__)


async def create_review_from_file_diffs(
    file_diffs: list[PullRequestFileChanges],
    review_id: int,
    review_status_id: int,
) -> None:
    """Create a pull request review from file diffs."""
    semaphore = asyncio.Semaphore(config.modules.reviews.max_concurrent_file_reviews)

    total_files = len(file_diffs)
    reviewed_files = 0

    review_tasks = [
        _review_file_diff(file_diff=file_diff, semaphore=semaphore)
        for file_diff in file_diffs
    ]
    review_per_file: dict[str, str] = {}
    for task in asyncio.as_completed(review_tasks):
        review_per_file |= await task

        reviewed_files += 1
        progress_value = int((reviewed_files / total_files) * 100)
        await api.update_progress(
            review_status_id,
            progress_value,
            ReviewStatus.processing,
        )

    patches_per_file = {file_diff.filename: file_diff.patch for file_diff in file_diffs}

    file_reviews = [
        FileReview(
            filename=filename,
            content=content,
            patch=patches_per_file.get(filename, ""),
        )
        for filename, content in review_per_file.items()
    ]
    await api.complete_review(
        review_id=review_id,
        review_status_id=review_status_id,
        file_reviews=file_reviews,
    )


async def _review_file_diff(
    file_diff: PullRequestFileChanges,
    semaphore: asyncio.Semaphore,
) -> dict[str, str]:
    """Create a review task for a single file.

    :param file_changes: The pull request file changes.
    :param semaphore: The semaphore.
    :return: A mapping from the file name to the review content.
    """
    answer = ""
    async with semaphore:
        review_content_iterator = await ReviewPullRequest.arun(request=file_diff)

        async for review_content in review_content_iterator:
            answer += review_content

    return {file_diff.filename: answer}
