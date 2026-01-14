import time
import requests
from typing import Optional

from sandwich.infrastructure.config import Settings
from sandwich.infrastructure.logging import get_logger
from sandwich.domain.exceptions import APIRequestError

logger = get_logger(__name__)


class BaseAPIClient:
    """Base API client with retry logic"""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def make_request(self, url: str) -> Optional[requests.Response]:
        """
        Make HTTP request with exponential backoff retry logic.

        Args:
            url: URL to request

        Returns:
            Response object or None if max retries exhausted
        """
        for attempt in range(self.settings.max_retries):
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    logger.warning(
                        f"Rate limited (429) on attempt {attempt + 1}, "
                        f"retrying in {2**attempt}s"
                    )
                    time.sleep(2**attempt)
                else:
                    logger.warning(
                        f"HTTP {response.status_code} error on attempt {attempt + 1}: {response.text}"
                    )
                    if attempt == self.settings.max_retries - 1:
                        raise APIRequestError(
                            f"HTTP {response.status_code} error: {response.text}"
                        )
                    time.sleep(2**attempt)
            except requests.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt == self.settings.max_retries - 1:
                    raise APIRequestError(
                        f"Request failed after {self.settings.max_retries} attempts: {e}"
                    )
                time.sleep(2**attempt)

        logger.error(f"Max retries ({self.settings.max_retries}) exhausted")
        return None
