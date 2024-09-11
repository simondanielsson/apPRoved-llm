import asyncio
import logging

from src.common.tools.review_pull_request import ReviewPullRequest
from src.reviews.dto.responses import PRReviewResponse
from src.reviews.models.pull_requests import FileReview, PullRequestFileChanges
from src.config import config
from src.utils.http import send_http_post_request

logger = logging.getLogger(__name__)


async def create_review_from_file_diffs(
    file_diffs: list[PullRequestFileChanges],
    review_id: int,
    review_status_id: int,
) -> None:
    """Create a pull request review from file diffs."""
    semaphore = asyncio.Semaphore(config.modules.reviews.max_concurrent_file_reviews)

    review_tasks = [
        _review_file_diff(file_diff=file_diff, semaphore=semaphore)
        for file_diff in file_diffs
    ]
    review_contents = await asyncio.gather(*review_tasks)
    file_names = [review.filename for review in file_diffs]

    review = PRReviewResponse(
        review_id=review_id,
        review_status_id=review_status_id,
        file_reviews=[
            FileReview(filename=filename, content=content)
            for filename, content in zip(file_names, review_contents)
        ],
    )
    url = f"{config.approved_api_url}/reviews/complete"
    await send_http_post_request(content=review.model_dump(), url=url)


async def _review_file_diff(
    file_diff: PullRequestFileChanges,
    semaphore: asyncio.Semaphore,
) -> str:
    """Create a review task for a single file.

    :param file_changes: The pull request file changes.
    :param semaphore: The semaphore.
    :return: The review content.
    """
    answer = ""
    async with semaphore:
        review_content_iterator = await ReviewPullRequest.arun(request=file_diff)

        async for review_content in review_content_iterator:
            answer += review_content

    return answer
