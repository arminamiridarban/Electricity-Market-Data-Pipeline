from app.client import fetch_latest_data, fetch_lastweek_data, fetch_period_data
from app.parser import clean_data
from app.exceptions import ApiRequestError
from app.logger import get_logger

logger = get_logger(__name__)


def get_data(mode="latest", start=None, end=None):
    """
    Fetches data from the API based on the specified mode and optional start/end parameters, then cleans and returns the data.
    Inputs:
    - mode: string indicating the data retrieval mode ('latest', 'lastweek', or 'period')
    - start: optional start datetime string for 'period' mode (e.g., '2026-03-15T10:30')
    - end: optional end datetime string for 'period' mode (e.g., '2026-03-16T10:30')
    Output: list of dictionaries containing the cleaned data with keys 'Time Stamp', 'MTU Start', 'Area', 'Value'
    """
    try:
        if mode == "latest":
            data = fetch_latest_data()
        elif mode == "lastweek":
            data = fetch_lastweek_data()
        elif mode == "period":
            if not start or not end:
                raise ValueError("Both 'start' and 'end' must be provided for period retrieval.")
            data = fetch_period_data(start=start, end=end)
        else:
            raise ValueError("Invalid mode. Choose 'latest', 'lastweek', or 'period'.")

        cleaned_data = clean_data(data)
        return cleaned_data

    except ValueError:
        raise
    except Exception as exc:
        logger.error("An error occurred while fetching or processing data: %s", exc)
        raise ApiRequestError("Failed to fetch data from the API.") from exc