"""HTTP utilities."""

import logging

import httpx

from src.config import config

logger = logging.getLogger(__name__)


async def send_http_post_request(content: dict, url: str) -> None:
    """Send."""
    timeout = httpx.Timeout(config.modules.common.request_timeout, read=None)

    async with httpx.AsyncClient() as client:
        try:
            callback = await client.post(
                url,
                timeout=timeout,
                json=content,
            )
            callback.raise_for_status()
        except httpx.HTTPStatusError as e:
            msg = "Failed to send HTTP request message."
            raise ValueError(
                msg,
            ) from e

    logger.info("Successfully sent HTTP request to %s", url)
