from src.reviews.dto.requests import CreateReviewFromFileDiffRequest
from src.reviews.services import pull_requests_service


async def create_review_from_file_diffs(message: dict) -> None:
    """Create a review from a file diff."""
    request = CreateReviewFromFileDiffRequest(**message)
    await pull_requests_service.create_review_from_file_diffs(
        file_diffs=request.file_diffs,
        review_id=request.review_id,
        review_status_id=request.review_status_id,
    )
