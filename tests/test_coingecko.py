import pytest
import json
from unittest.mock import Mock, patch, call
from pathlib import Path
from tests.fixtures.coingecko_fixtures import (
    get_coingecko_page_data,
    get_coingecko_rate_limit_response,
    get_coingecko_error_response,
    get_coingecko_empty_response,
)


@pytest.mark.unit
class TestMakeRequest:
    def test_successful_request(self):
        from sandwich.coingecko.markets import make_request

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test content"

        with patch(
            "sandwich.coingecko.markets.requests.get", return_value=mock_response
        ):
            result = make_request("https://api.coingecko.com/api/v3/test")
            assert result.status_code == 200
            assert result.content == b"test content"

    def test_rate_limit_with_retry(self):
        from sandwich.coingecko.markets import make_request

        mock_rate_limit = Mock()
        mock_rate_limit.status_code = 429

        mock_success = Mock()
        mock_success.status_code = 200
        mock_success.content = b"success"

        with patch("sandwich.coingecko.markets.requests.get") as mock_get:
            mock_get.side_effect = [mock_rate_limit, mock_rate_limit, mock_success]
            result = make_request(
                "https://api.coingecko.com/api/v3/test", max_retries=3
            )
            assert result.status_code == 200
            assert mock_get.call_count == 3

    def test_max_retries_exhausted(self):
        from sandwich.coingecko.markets import make_request

        mock_rate_limit = Mock()
        mock_rate_limit.status_code = 429

        with patch(
            "sandwich.coingecko.markets.requests.get", return_value=mock_rate_limit
        ):
            result = make_request(
                "https://api.coingecko.com/api/v3/test", max_retries=5
            )
            assert result is None

    def test_network_error(self):
        from sandwich.coingecko.markets import make_request
        import requests

        with patch(
            "sandwich.coingecko.markets.requests.get",
            side_effect=requests.ConnectionError(),
        ):
            with pytest.raises(requests.ConnectionError):
                make_request("https://api.coingecko.com/api/v3/test")


@pytest.mark.unit
class TestDownloadFile:
    def test_successful_download(self, tmp_path):
        from sandwich.coingecko.markets import download_file

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test file content"

        file_path = tmp_path / "test_file.json"

        with patch(
            "sandwich.coingecko.markets.make_request", return_value=mock_response
        ):
            download_file("https://example.com/file.json", str(file_path))

            assert file_path.exists()
            with open(file_path, "rb") as f:
                assert f.read() == b"test file content"

    def test_http_404_error(self, tmp_path, capsys):
        from sandwich.coingecko.markets import download_file

        mock_response = Mock()
        mock_response.status_code = 404

        file_path = tmp_path / "test_file.json"

        with patch(
            "sandwich.coingecko.markets.make_request", return_value=mock_response
        ):
            download_file("https://example.com/file.json", str(file_path))

            captured = capsys.readouterr()
            assert "Request failed with status code: 404" in captured.out
            assert not file_path.exists()

    def test_permission_denied_on_write(self, tmp_path, capsys):
        from sandwich.coingecko.markets import download_file

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test content"

        file_path = tmp_path / "readonly" / "test.json"
        (tmp_path / "readonly").mkdir()

        with patch(
            "sandwich.coingecko.markets.make_request", return_value=mock_response
        ):
            with patch(
                "builtins.open", side_effect=PermissionError("Permission denied")
            ):
                download_file("https://example.com/file.json", str(file_path))

    def test_invalid_file_path(self, tmp_path):
        from sandwich.coingecko.markets import download_file

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test content"

        with patch(
            "sandwich.coingecko.markets.make_request", return_value=mock_response
        ):
            download_file("https://example.com/file.json", "/invalid/path/file.json")


@pytest.mark.unit
class TestSaveMarketData:
    def test_single_page_fetch(self, tmp_path, capsys):
        from sandwich.coingecko.markets import save_market_data

        page1_data = get_coingecko_page_data(1)
        page2_data = []

        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = page1_data

        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = page2_data

        file_path = tmp_path / "marketcap.json"

        with patch("sandwich.coingecko.markets.make_request") as mock_make:
            mock_make.side_effect = [mock_response1, mock_response2]
            save_market_data(str(file_path))

            captured = capsys.readouterr()
            assert "Number of items in the list: 3" in captured.out
            assert f"Market data saved successfully to {file_path}" in captured.out

            with open(file_path, "r") as f:
                data = json.loads(f.read())
                assert len(data) == 3

    def test_page_request_failure(self, tmp_path, capsys):
        from sandwich.coingecko.markets import save_market_data

        page1_data = get_coingecko_page_data(1)

        mock_success = Mock()
        mock_success.status_code = 200
        mock_success.json.return_value = page1_data

        mock_error = Mock()
        mock_error.status_code = 500

        file_path = tmp_path / "marketcap.json"

        with patch("sandwich.coingecko.markets.make_request") as mock_make_request:
            mock_make_request.side_effect = [mock_success, mock_error]
            save_market_data(str(file_path))

            captured = capsys.readouterr()
            assert "Request failed for page 2 with status code: 500" in captured.out

    def test_file_write_error(self, tmp_path, capsys):
        from sandwich.coingecko.markets import save_market_data

        page1_data = get_coingecko_page_data(1)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = page1_data

        file_path = tmp_path / "marketcap.json"

        with patch(
            "sandwich.coingecko.markets.make_request", return_value=mock_response
        ):
            with patch(
                "builtins.open", side_effect=PermissionError("Permission denied")
            ):
                save_market_data(str(file_path))
