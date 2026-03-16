from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

from app.config import DATASET_BASE_URL, DATASET_NAME, DEFAULT_TIMEOUT
from app.exceptions import ApiRequestError, InvalidApiResponseError
from app.logger import get_logger


logger = get_logger(__name__)


def _build_endpoint(mode: str) -> str:
    if mode not in {"latest", "lastweek", "period"}:
        raise ValueError(
            f"Invalid endpoint type: {mode}. Allowed types are: latest, lastweek, period."
        )
    return f"{DATASET_BASE_URL}/{DATASET_NAME}/{mode}"


def _normalize_datetime(value: str) -> str:
    """
    Normalize a datetime string to UTC ISO-8601 format expected by the API.

    Accepted examples:
    - 2026-03-15T10:30
    - 2026-03-15 10:30
    - 2026-03-15T10:30:00
    - 2026-03-15T10:30:00Z
    - 2026-03-15T10:30:00+01:00
    """
    if not value or not value.strip():
        raise ValueError("Datetime value cannot be empty.")

    raw = value.strip().replace(" ", "T")

    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(
            f"Invalid datetime format: '{value}'. Use ISO-like format such as "
            f"'2026-03-15T10:30' or '2026-03-15T10:30:00Z'."
        ) from exc

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def send_request_to_api(endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    try:
        response = requests.get(endpoint, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.Timeout as exc:
        logger.exception("Request timed out for endpoint=%s params=%s", endpoint, params)
        raise ApiRequestError("The API request timed out.") from exc
    except requests.ConnectionError as exc:
        logger.exception("Connection error for endpoint=%s params=%s", endpoint, params)
        raise ApiRequestError("A network connection error occurred while calling the API.") from exc
    except requests.HTTPError as exc:
        logger.exception(
            "HTTP error for endpoint=%s params=%s status=%s body=%s",
            endpoint,
            params,
            exc.response.status_code if exc.response else None,
            exc.response.text if exc.response else None,
        )
        raise ApiRequestError(
            f"API returned HTTP {exc.response.status_code if exc.response else 'unknown'}."
        ) from exc
    except requests.RequestException as exc:
        logger.exception("Unexpected request error for endpoint=%s params=%s", endpoint, params)
        raise ApiRequestError("An unexpected API request error occurred.") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        logger.exception("Invalid JSON response for endpoint=%s params=%s", endpoint, params)
        raise InvalidApiResponseError("The API response was not valid JSON.") from exc

    if not isinstance(payload, dict):
        logger.error("Unexpected JSON type: %s", type(payload).__name__)
        raise InvalidApiResponseError("The API response JSON must be an object.")

    return payload


def fetch_latest_data() -> Dict[str, Any]:
    endpoint = _build_endpoint("latest")
    logger.info("Fetching latest data from %s", endpoint)
    return send_request_to_api(endpoint)


def fetch_lastweek_data() -> Dict[str, Any]:
    endpoint = _build_endpoint("lastweek")
    logger.info("Fetching lastweek data from %s", endpoint)
    return send_request_to_api(endpoint)


def fetch_period_data(start: str, end: str) -> Dict[str, Any]:
    if not start or not end:
        raise ValueError("Both 'start' and 'end' must be provided for period retrieval.")

    start_iso = _normalize_datetime(start)
    end_iso = _normalize_datetime(end)

    start_dt = datetime.strptime(start_iso, "%Y-%m-%dT%H:%M:%SZ")
    end_dt = datetime.strptime(end_iso, "%Y-%m-%dT%H:%M:%SZ")

    if end_dt < start_dt:
        raise ValueError("'end' must be greater than or equal to 'start'.")

    endpoint = _build_endpoint("period")
    params = {
        "from": start_iso,
        "to": end_iso,
    }

    logger.info("Fetching period data from %s with params=%s", endpoint, params)
    return send_request_to_api(endpoint, params=params)


