from pydantic import BaseModel


class PullRequestFileChanges(BaseModel):
    """Changes made to a file in a pull request."""

    filename: str
    patch: str
    additions: int
    deletions: int
    changes: int


class FileReview(BaseModel):
    """Review of a file in a pull request.

    Attributes:
        - filename: The name of the file.
        - content: The content of the review.
    """

    filename: str
    content: str
