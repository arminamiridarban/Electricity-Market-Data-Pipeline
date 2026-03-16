import pytest, requests
from app.client import _normalize_datetime, fetch_latest_data, send_request_to_api, _build_endpoint, fetch_period_data, fetch_lastweek_data
from unittest.mock import MagicMock, patch
from app.exceptions import ApiRequestError, InvalidApiResponseError

def test_build_endpoint_latest():
    result = _build_endpoint("latest")
    assert result == "https://electricitymarketservice.energinet.dk/api/v1/PublicData/dataset/mfrrRequest/latest"


def test_build_endpoint_lastweek():
    result = _build_endpoint("lastweek")
    assert result == "https://electricitymarketservice.energinet.dk/api/v1/PublicData/dataset/mfrrRequest/lastweek"

def test_build_endpoint_period():
    result = _build_endpoint("period")
    assert result == "https://electricitymarketservice.energinet.dk/api/v1/PublicData/dataset/mfrrRequest/period"

def test_build_endpoint_invalid():
    with pytest.raises(ValueError, match="Invalid endpoint type: invalid. Allowed types are: latest, lastweek, period."):
        _build_endpoint("invalid")


def test_normalize_datetime():
    assert _normalize_datetime("2024-01-01") == "2024-01-01T00:00:00Z"
    assert _normalize_datetime("2024-01-01T12:30:45") == "2024-01-01T12:30:45Z"
    assert _normalize_datetime("2024-01-01 12:30:45") == "2024-01-01T12:30:45Z"
    assert _normalize_datetime("2024-01-01 12:30:45Z") == "2024-01-01T12:30:45Z"
    with pytest.raises(ValueError):
        _normalize_datetime("invalid-date")
    with pytest.raises(ValueError):
        _normalize_datetime("2026-03-15T10:300")

def test_normalized_datetime_with_empty_values():
    with pytest.raises(ValueError, match="Datetime value cannot be empty."):
        _normalize_datetime("")
    with pytest.raises(ValueError, match="Datetime value cannot be empty."):
        _normalize_datetime("   ")

def test_send_request_success():
    
    fake_response = MagicMock()
    fake_response.json.return_value = {"mfrrRequest": []}
    fake_response.raise_for_status.return_value = None

    with patch("app.client.requests.get", return_value=fake_response):

        result = send_request_to_api("http://fake-url")

        assert result == {"mfrrRequest": []}

def test_send_request_timeout():
    with patch("app.client.requests.get", side_effect=requests.Timeout):
        with pytest.raises(ApiRequestError):
            send_request_to_api("http://fake-url")

def test_send_request_conection_error():
    with patch("app.client.requests.get", side_effect=requests.ConnectionError):
        with pytest.raises(ApiRequestError):
            send_request_to_api("http://fake-url")

def test_send_request_HTTP_error():
    fake_response = MagicMock()
    fake_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

    with patch("app.client.requests.get", return_value=fake_response):
        with pytest.raises(ApiRequestError):
            send_request_to_api("http://fake-url")

def test_send_request_invalid_json():
    fake_response = MagicMock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.side_effect = ValueError("No JSON object could be decoded")

    with patch("app.client.requests.get", return_value=fake_response):
        with pytest.raises(InvalidApiResponseError):
            send_request_to_api("http://fake-url")

def test_send_request_non_dict_json():
    fake_response = MagicMock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = ["not", "a", "dict"]

    with patch("app.client.requests.get", return_value=fake_response):
        with pytest.raises(InvalidApiResponseError, match="The API response JSON must be an object."):
            send_request_to_api("http://fake-url")

def test_fetch_latest_calls_correct_endpoint():
    with patch("app.client.send_request_to_api") as mock_send:
        mock_send.return_value = {"mfrrRequest": []}

        result = fetch_latest_data()

        mock_send.assert_called_once()
        assert result == {"mfrrRequest": []}
        
def test_fetch_lastweek_calls_correct_endpoint():
    with patch("app.client.send_request_to_api") as mock_send:
        mock_send.return_value = {"mfrrRequest": []}

        result = fetch_lastweek_data()

        mock_send.assert_called_once()
        assert result == {"mfrrRequest": []}

def test_fetch_period_calls_correct_endpoint():
    with patch("app.client.send_request_to_api") as mock_send:
        mock_send.return_value = {"mfrrRequest": []}

        result = fetch_period_data("2024-01-01", "2024-01-31")

        mock_send.assert_called_once()
        assert result == {"mfrrRequest": []}