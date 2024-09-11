"""Request DTOs for the reviews module."""

from pydantic import BaseModel

from src.reviews.models.pull_requests import PullRequestFileChanges


class CreateReviewFromFileDiffRequest(BaseModel):
    """Request to create a review from a file diff."""

    review_id: int
    review_status_id: int
    file_diffs: list[PullRequestFileChanges]
