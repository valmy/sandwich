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
            Response object

        Raises:
            APIRequestError: If API request fails after all retries
        """
        # Validate URL to prevent SSRF attacks
        from urllib.parse import urlparse
        import ipaddress

        parsed = urlparse(url)
        if not parsed.scheme or parsed.scheme not in ["http", "https"]:
            raise APIRequestError("Invalid URL scheme")
        if not parsed.netloc:
            raise APIRequestError("Invalid URL")

        try:
            # Check if hostname is an IP address
            ip = ipaddress.ip_address(parsed.hostname or "")
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                raise APIRequestError("Access to internal networks not allowed")
        except ValueError:
            # Not an IP address, check for localhost/internal hostnames
            hostname = (parsed.hostname or "").lower()
            if (
                hostname in ["localhost", "127.0.0.1", "::1"]
                or hostname.startswith("10.")
                or hostname.startswith("192.168.")
                or hostname.startswith("172.")
            ):
                raise APIRequestError("Access to internal networks not allowed")

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
                    if attempt < self.settings.max_retries - 1:
                        time.sleep(2**attempt)
                else:
                    logger.warning(
                        f"HTTP {response.status_code} error on attempt {attempt + 1}: [Response content hidden for security]"
                    )
                    if attempt < self.settings.max_retries - 1:
                        time.sleep(2**attempt)
            except requests.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {e}")
                if attempt < self.settings.max_retries - 1:
                    time.sleep(2**attempt)

        logger.error(f"Max retries ({self.settings.max_retries}) exhausted")
        raise APIRequestError(f"Request failed after {self.settings.max_retries} attempts")
