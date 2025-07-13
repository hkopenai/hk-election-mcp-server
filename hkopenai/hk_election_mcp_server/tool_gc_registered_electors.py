"""
Module for fetching and processing data on registered electors in Hong Kong's geographical constituencies.

This module provides functions to retrieve and parse data from the voter registration website
to get the number of registered electors for specified year ranges.
"""

import csv
import io
from typing import Dict, List
import requests
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


def fetch_gc_registered_electors_data(start_year: int, end_year: int) -> List[Dict]:
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
        if current_year not in data_dict:
            csv_data = try_fetch_year_data(current_year)
            if csv_data:
                for year, count in csv_data.items():
                    if year not in data_dict:
                        data_dict[year] = count
            else:
                # If no data for the specific year CSV, try nearby years for multi-year data
                for offset in [-1, 1, -2, 2]:
                    test_year = current_year + offset
                    if test_year >= 2009 and test_year <= end_year:
                        csv_data = try_fetch_year_data(test_year)
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


def try_fetch_year_data(year: int) -> Dict[int, int]:
    """
    Attempt to fetch data for a specific year, trying both URL formats.
    Returns a dictionary of year to elector count.
    """
    urls = [
        f"https://www.voterregistration.gov.hk/eng/psi/csv/{year}_gc-no-of-registered-electors.csv",
        f"https://www.voterregistration.gov.hk/eng/psi/csv/{year}_gc-no-of-registered-electors_en.csv",
    ]

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Handle UTF-8 with BOM
                content = response.content.decode("utf-8-sig")
                return parse_csv(content)
        except (requests.exceptions.RequestException, UnicodeDecodeError):
            continue
    return {}


def parse_csv(content: str) -> Dict[int, int]:
    """
    Parse CSV content to extract year and number of registered electors.
    """
    result = {}
    reader = csv.reader(io.StringIO(content))
    next(reader, None)  # Skip header if exists

    for row in reader:
        if len(row) >= 2:
            try:
                year = int(row[0].strip())
                count = int(row[1].strip().replace(",", ""))
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
    data = fetch_gc_registered_electors_data(start_year, end_year)
    if "error" in data[0]:
        return {"error": data[0]["error"]}
    return {
        "data": data,
        "source": "Registration and Electoral Office",
        "note": "Data fetched from voterregistration.gov.hk",
    }

