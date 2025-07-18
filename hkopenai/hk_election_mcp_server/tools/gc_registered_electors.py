"""
Module for fetching and processing data on registered electors in Hong Kong's geographical constituencies.

This module provides functions to retrieve and parse data from the voter registration website
to get the number of registered electors for specified year ranges.
"""

import csv
import io
from typing import Dict, List
from hkopenai_common.csv_utils import fetch_csv_from_url
from pydantic import Field
from typing_extensions import Annotated


def register(mcp):
    """Registers the registered electors tool with the FastMCP server."""

    @mcp.tool(
        description="Get the number of registered electors in Hong Kong's geographical constituencies by year range",
    )
    def get_gc_registered_electors(
        start_year: Annotated[int, Field(description="Start year for data range")],
        end_year: Annotated[int, Field(description="End year for data range")],
    ) -> Dict:
        """Get the number of registered electors in Hong Kong's geographical constituencies by year range.

        Args:
            start_year (int): Start year of the range (minimum 2009)
            end_year (int): End year of the range

        Returns:
            Dictionary containing the data list, source, and note
        """
        return _get_gc_registered_electors(start_year, end_year)


def _fetch_gc_registered_electors_data(start_year: int, end_year: int) -> List[Dict] | Dict[str, str]:
    """
    Fetch and aggregate data on the number of registered electors in Hong Kong's geographical constituencies
    for the given year range.
    """
    if start_year < 2009:
        return [{"error": "Start year must be 2009 or later"}]
    if start_year > end_year:
        return [{"error": "Start year must be less than or equal to end year"}]

    data_dict: Dict[int, int] = {}
    current_year = start_year

    while current_year <= end_year:
        csv_data = _try_fetch_year_data(current_year)
        if "error" in csv_data:
            return csv_data  # Propagate the error
        if csv_data:
            for year, count in csv_data.items():
                if year not in data_dict:
                    data_dict[year] = count
        else:
            # If no data for the specific year CSV, try nearby years for multi-year data
            for offset in [-1, 1, -2, 2]:
                test_year = current_year + offset
                if test_year >= 2009 and test_year <= end_year:
                    csv_data = _try_fetch_year_data(test_year)
                    if "error" in csv_data:
                        return csv_data  # Propagate the error
                    if csv_data and current_year in csv_data:
                        data_dict[current_year] = csv_data[current_year]
                        break
        current_year += 1

    result = [
        {"year": year, "electors": count}
        for year, count in sorted(data_dict.items())
        if start_year <= year <= end_year
    ]

    if not result:
        return [{"error": "No data found for the specified year range"}]

    return result


def _try_fetch_year_data(year: int) -> Dict[int, int] | Dict[str, str]:
    """
    Attempt to fetch data for a specific year, trying both URL formats.
    Returns a dictionary of year to elector count.
    """
    urls = [
        f"https://www.voterregistration.gov.hk/eng/psi/csv/{year}_gc-no-of-registered-electors.csv",
        f"https://www.voterregistration.gov.hk/eng/psi/csv/{year}_gc-no-of-registered-electors_en.csv",
    ]

    for url in urls:
        csv_data = fetch_csv_from_url(url, encoding="utf-8-sig", timeout=10)
        if "error" in csv_data:
            return csv_data  # Propagate the error
        if csv_data:
            return _parse_csv_data(csv_data)
    return {}


def _parse_csv_data(data: List[Dict]) -> Dict[int, int]:
    """
    Parse CSV content to extract year and number of registered electors.
    """
    result = {}
    for row in data:
        if len(row) >= 2:
            try:
                # Assuming the first column is year and second is count
                year_key = list(row.keys())[0]
                count_key = list(row.keys())[1]
                year = int(row[year_key].strip())
                count = int(row[count_key].strip().replace(",", ""))
                result[year] = count
            except (ValueError, IndexError):
                continue
    return result


def _get_gc_registered_electors(start_year: int = 2009, end_year: int = 2024) -> Dict:
    """
    Get the number of registered electors in Hong Kong's geographical constituencies by year range.

    Args:
        start_year (int): Start year of the range (minimum 2009)
        end_year (int): End year of the range

    Returns:
        Dictionary containing the data list, source, and note
    """
    data = _fetch_gc_registered_electors_data(start_year, end_year)
    if "error" in data[0]:
        return {"error": data[0]["error"]}
    return {
        "data": data,
        "source": "Registration and Electoral Office",
        "note": "Data fetched from voterregistration.gov.hk",
    }
