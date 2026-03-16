class ApiRequestError(Exception):
    """Raised when the API request fails."""
    pass


class InvalidApiResponseError(Exception):
    """Raised when API response structure is invalid."""
    pass


