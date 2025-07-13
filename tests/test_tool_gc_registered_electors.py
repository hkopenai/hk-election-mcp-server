"""
Unit tests for the GC Registered Electors tool.

This module tests the functionality of fetching and parsing data related to
registered electors in Hong Kong's geographical constituencies.
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
from hkopenai.hk_election_mcp_server.tool_gc_registered_electors import (
    fetch_gc_registered_electors_data,
    try_fetch_year_data,
    parse_csv,
    register,
)


class TestGCRegisteredElectors(unittest.TestCase):
    """
    Test class for verifying the functionality of the GC Registered Electors tool.
    
    This class contains test cases to ensure the correct parsing, fetching, and
    processing of data related to registered electors in Hong Kong.
    """
    def test_parse_csv_valid_data(self):
        """Test parsing of CSV content with valid data."""
        csv_content = "Year,No. of Registered Electors\n2015,3693942\n2016,3779085"
        result = parse_csv(csv_content)
        expected = {2015: 3693942, 2016: 3779085}
        self.assertEqual(result, expected)

    def test_parse_csv_invalid_data(self):
        """Test parsing of CSV content with invalid data."""
        csv_content = "Year,No. of Registered Electors\nInvalid,Data\n2015,3693942"
        result = parse_csv(csv_content)
        expected = {2015: 3693942}
        self.assertEqual(result, expected)

    @patch("hkopenai.hk_election_mcp_server.tool_gc_registered_electors.requests.get")
    def test_try_fetch_year_data_success(self, mock_get):
        """Test fetching data for a year with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = (
            b"\xef\xbb\xbfYear,No. of Registered Electors\n2015,3693942"
        )
        mock_get.return_value = mock_response

        result = try_fetch_year_data(2015)
        expected = {2015: 3693942}
        self.assertEqual(result, expected)

    @patch("hkopenai.hk_election_mcp_server.tool_gc_registered_electors.requests.get")
    def test_try_fetch_year_data_failure(self, mock_get):
        """Test fetching data for a year with failed response."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = try_fetch_year_data(2015)
        expected = {}
        self.assertEqual(result, expected)

    def test_fetch_gc_registered_electors_data_invalid_range(self):
        """Test fetching data with invalid year range."""
        result = fetch_gc_registered_electors_data(2020, 2010)
        self.assertEqual(
            result, [{"error": "Start year must be less than or equal to end year"}]
        )

        result = fetch_gc_registered_electors_data(2008, 2010)
        self.assertEqual(result, [{"error": "Start year must be 2009 or later"}])

    @patch(
        "hkopenai.hk_election_mcp_server.tool_gc_registered_electors.try_fetch_year_data"
    )
    def test_fetch_gc_registered_electors_data_valid_range(self, mock_fetch):
        """Test fetching data with valid year range."""
        mock_fetch.side_effect = [
            {2015: 3693942, 2016: 3779085},
            {2016: 3779085, 2017: 3805069},
        ]
        result = fetch_gc_registered_electors_data(2015, 2017)
        expected = [
            {"year": 2015, "electors": 3693942},
            {"year": 2016, "electors": 3779085},
            {"year": 2017, "electors": 3805069},
        ]
        self.assertEqual(result, expected)

    def test_register_tool(self):
        """
        Test the registration of the get_gc_registered_electors tool.

        This test verifies that the register function correctly registers the tool
        with the FastMCP server and that the registered tool calls the underlying
        _get_gc_registered_electors function.
        """
        mock_mcp = MagicMock()

        # Call the register function
        register(mock_mcp)

        # Verify that mcp.tool was called with the correct description
        mock_mcp.tool.assert_called_once_with(
            description="Get the number of registered electors in Hong Kong's geographical constituencies by year range",
        )

        # Get the mock that represents the decorator returned by mcp.tool
        mock_decorator = mock_mcp.tool.return_value

        # Verify that the mock decorator was called once (i.e., the function was decorated)
        mock_decorator.assert_called_once()

        # The decorated function is the first argument of the first call to the mock_decorator
        decorated_function = mock_decorator.call_args[0][0]

        # Verify the name of the decorated function
        self.assertEqual(decorated_function.__name__, "get_gc_registered_electors")

        # Call the decorated function and verify it calls _get_gc_registered_electors
        with patch(
            "hkopenai.hk_election_mcp_server.tool_gc_registered_electors._get_gc_registered_electors"
        ) as mock_get_gc_registered_electors:
            decorated_function(start_year=2018, end_year=2019)
            mock_get_gc_registered_electors.assert_called_once_with(2018, 2019)
