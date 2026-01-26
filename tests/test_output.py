"""Tests for output formatting."""

import pytest
from sandwich.application.output import OutputFormatter, OutputFormat
from sandwich.domain.exceptions import SandwichError, ValidationError


class TestOutputFormatter:
    """Tests for OutputFormatter class."""

    def test_text_format_success_with_message(self):
        """Test text format success with message."""
        formatter = OutputFormatter(OutputFormat.TEXT)
        result = formatter.format_success(None, "Operation completed")
        assert result == "Operation completed"

    def test_text_format_success_with_data(self):
        """Test text format success with data."""
        formatter = OutputFormatter(OutputFormat.TEXT)
        result = formatter.format_success([1, 2, 3])
        assert result == "[1, 2, 3]"

    def test_text_format_error(self):
        """Test text format error."""
        formatter = OutputFormatter(OutputFormat.TEXT)
        error = Exception("Something went wrong")
        result = formatter.format_error(error)
        assert "Error: Something went wrong" in result

    def test_text_format_error_with_message(self):
        """Test text format error with message."""
        formatter = OutputFormatter(OutputFormat.TEXT)
        error = Exception("Something went wrong")
        result = formatter.format_error(error, "Operation failed")
        assert "Error: Operation failed" in result
        assert "Something went wrong" in result

    def test_json_format_success_with_message(self):
        """Test JSON format success with message."""
        formatter = OutputFormatter(OutputFormat.JSON)
        result = formatter.format_success(None, "Operation completed")
        assert "success" in result
        assert "true" in result
        assert "message" in result
        assert "Operation completed" in result
        assert "data" in result
        assert "null" in result

    def test_json_format_success_with_data(self):
        """Test JSON format success with data."""
        formatter = OutputFormatter(OutputFormat.JSON)
        data = {"key": "value", "numbers": [1, 2, 3]}
        result = formatter.format_success(data, "Operation completed")
        assert "success" in result
        assert "true" in result
        assert "message" in result
        assert "Operation completed" in result
        assert "data" in result
        assert "key" in result
        assert "value" in result

    def test_json_format_error(self):
        """Test JSON format error."""
        formatter = OutputFormatter(OutputFormat.JSON)
        error = Exception("Something went wrong")
        result = formatter.format_error(error)
        assert "success" in result
        assert "false" in result
        assert "error" in result
        assert "Something went wrong" in result

    def test_json_format_error_with_message(self):
        """Test JSON format error with message."""
        formatter = OutputFormatter(OutputFormat.JSON)
        error = Exception("Something went wrong")
        result = formatter.format_error(error, "Operation failed")
        assert "success" in result
        assert "false" in result
        assert "message" in result
        assert "Operation failed" in result
        assert "error" in result
        assert "Something went wrong" in result

    def test_json_format_sandwich_error_with_details(self):
        """Test JSON format for SandwichError with details."""
        formatter = OutputFormatter(OutputFormat.JSON)
        error = ValidationError("field", "invalid value", "Detailed error info")
        result = formatter.format_error(error, "Validation failed")
        assert "success" in result
        assert "false" in result
        assert "message" in result
        assert "Validation failed" in result
        assert "error" in result
        assert "Validation error for 'field'" in result
        assert "details" in result
        assert "Detailed error info" in result
