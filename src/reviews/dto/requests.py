"""Request DTOs for the reviews module."""

from pydantic import BaseModel

from src.reviews.models.pull_requests import FileReview, PullRequestFileChanges


class CreateReviewFromFileDiffRequest(BaseModel):
    """Request to create a review from a file diff."""

    review_id: int
    review_status_id: int
    file_diffs: list[PullRequestFileChanges]


class UpdateProgressRequest(BaseModel):
    """Request to update the progress of a review."""

    progress: int
    status: str


class CompleteReviewRequest(BaseModel):
    """Request to complete a review."""

    review_id: int
    review_status_id: int
    file_reviews: list[FileReview]
