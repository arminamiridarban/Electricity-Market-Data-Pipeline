import os

DATASET_BASE_URL = r"https://electricitymarketservice.energinet.dk/api/v1/PublicData/dataset"
DATASET_NAME = "mfrrRequest"
DEFAULT_TIMEOUT = int(os.getenv("API_TIMEOUT", 10))

ALLOWED_SCHEDULE_INTERVALS = [1, 5, 15]
DEFAULT_SCHEDULE_INTERVAL = 1

def getScheduleMinutes() -> int:
    raw_value = os.getenv("SCHEDULE_INTERVAL", str(DEFAULT_SCHEDULE_INTERVAL))

    try:
        schedule = int(raw_value)
    except ValueError as e:
        raise ValueError(
            f"Invalid SCHEDULE_INTERVAL value: {raw_value}. Must be an integer."
        ) from e

    if schedule not in ALLOWED_SCHEDULE_INTERVALS:
        raise ValueError(
            f"Invalid SCHEDULE_INTERVAL value: {schedule}. Allowed values are: {ALLOWED_SCHEDULE_INTERVALS}."
        )
    
    return schedule