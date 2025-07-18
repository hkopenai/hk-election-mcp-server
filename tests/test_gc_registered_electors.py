"""
Module for testing the registered electors tool functionality.

This module contains unit tests for fetching and processing registered electors data.
"""

import unittest
from unittest.mock import patch, MagicMock

from hkopenai.hk_election_mcp_server.tools.gc_registered_electors import (
    _get_gc_registered_electors,
    register,
)


class TestGCRegisteredElectors(unittest.TestCase):
    """
    Test class for verifying registered electors functionality.

    This class contains test cases to ensure the data fetching and processing
    for registered electors data work as expected.
    """

    @patch(
        "hkopenai.hk_election_mcp_server.tools.gc_registered_electors._try_fetch_year_data"
    )
    def test_get_gc_registered_electors(self, mock_try_fetch_year_data):
        """
        Test the retrieval and aggregation of registered electors data.

        This test verifies that the function correctly fetches and aggregates data
        for a given year range, handles missing years, and propagates errors.
        """
        # Mock data for _try_fetch_year_data
        mock_try_fetch_year_data.side_effect = lambda year: {
            2019: {2019: 3800000},
            2020: {2020: 4000000},
            2022: {2022: 4200000},
        }.get(year, {})

        # Test successful data retrieval for a range
        result = _get_gc_registered_electors(2019, 2022)
        self.assertIn("data", result)
        self.assertIn("source", result)
        self.assertIn("note", result)
        self.assertEqual(len(result["data"]), 3)  # 2019, 2020, 2022
        self.assertEqual(result["data"][0]["year"], 2019)
        self.assertEqual(result["data"][0]["electors"], 3800000)

        # Test error handling when _try_fetch_year_data returns an error
        mock_try_fetch_year_data.side_effect = [
            {"error": "Fetch failed"}
        ]
        result = _get_gc_registered_electors(2019, 2019)
        self.assertEqual(result, {"error": "Fetch failed"})

        # Test invalid start year
        mock_try_fetch_year_data.side_effect = [] # Reset mock
        result = _get_gc_registered_electors(2000, 2010)
        self.assertEqual(result, {"error": "Start year must be 2009 or later"})

        # Test start year greater than end year
        mock_try_fetch_year_data.side_effect = [] # Reset mock
        result = _get_gc_registered_electors(2010, 2009)
        self.assertEqual(result, {"error": "Start year must be less than or equal to end year"})

        # Test no data found for the specified range
        mock_try_fetch_year_data.side_effect = lambda year: {}
        result = _get_gc_registered_electors(2023, 2024)
        self.assertEqual(result, {"error": "No data found for the specified year range"})

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
            description="Get the number of registered electors in Hong Kong's geographical constituencies by year range"
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
            "hkopenai.hk_election_mcp_server.tools.gc_registered_electors._get_gc_registered_electors"
        ) as mock_get_gc_registered_electors:
            decorated_function(start_year=2018, end_year=2019)
            mock_get_gc_registered_electors.assert_called_once_with(2018, 2019)
