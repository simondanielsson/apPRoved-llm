from pydantic import BaseModel

from src.reviews.models.pull_requests import FileReview


class PRReviewResponse(BaseModel):
    """Response for a pull request review."""

    review_id: int
    review_status_id: int
    file_reviews: list[FileReview]
