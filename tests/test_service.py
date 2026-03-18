import pytest
from app.exceptions import ApiRequestError
from app.service import get_data
from unittest.mock import patch

def test_get_data_period_without_start_raises_value_error():
    with pytest.raises(ValueError, match="Both 'start' and 'end' must be provided"):
        get_data(mode="period", start=None, end="2026-03-15T11:00:00")


def test_get_data_period_without_end_raises_value_error():
    with pytest.raises(ValueError, match="Both 'start' and 'end' must be provided"):
        get_data(mode="period", start="2026-03-15T10:00:00", end=None)

def test_get_data_invalid_mode_raises_value_error():
    with pytest.raises(ValueError, match="Invalid mode"):
        get_data(mode="dummy_mode")


def test_get_data_wraps_unexpected_error_in_api_request_error():
    with patch("app.service.fetch_latest_data", side_effect=Exception("Boom")):
        with pytest.raises(ApiRequestError, match="Failed to fetch data from the API."):
            get_data(mode="latest")

def test_get_data_period_returns_cleaned_data():
    raw_data = {"mfrrRequest": [{"dummy": "value"}]}
    cleaned_data = [{"Area": "DK1", "Value": 75}]

    with patch("app.service.fetch_period_data", return_value=raw_data) as mock_fetch, patch("app.service.clean_data", return_value=cleaned_data) as mock_clean:

        result = get_data(
            mode="period",
            start="2026-03-15T10:00:00",
            end="2026-03-15T11:00:00",
        )

        assert result == cleaned_data
        mock_fetch.assert_called_once_with(
            start="2026-03-15T10:00:00",
            end="2026-03-15T11:00:00",
        )
        mock_clean.assert_called_once_with(raw_data)

def test_get_data_latest_returns_cleaned_data():
    raw_data = {"mfrrRequest": [{"dummy": "value"}]}
    cleaned_data = [{"Area": "DK1", "Value": 100}]

    with patch("app.service.fetch_latest_data", return_value=raw_data) as mock_fetch, \
         patch("app.service.clean_data", return_value=cleaned_data) as mock_clean:

        result = get_data(mode="latest")

        assert result == cleaned_data
        mock_fetch.assert_called_once()
        mock_clean.assert_called_once_with(raw_data)


def test_get_data_lastweek_returns_cleaned_data():
    raw_data = {"mfrrRequest": [{"dummy": "value"}]}
    cleaned_data = [{"Area": "DK2", "Value": 50}]

    with patch("app.service.fetch_lastweek_data", return_value=raw_data) as mock_fetch, \
         patch("app.service.clean_data", return_value=cleaned_data) as mock_clean:

        result = get_data(mode="lastweek")

        assert result == cleaned_data
        mock_fetch.assert_called_once()
        mock_clean.assert_called_once_with(raw_data)