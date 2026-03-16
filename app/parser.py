from app.logger import get_logger
logger = get_logger(__name__)

def clean_data(data):

    if not data:
        raise ValueError("Data is empty or None.")

    if "mfrrRequest" not in data or not isinstance(data["mfrrRequest"], list):
        raise ValueError("Invalid input data: expected a payload with an 'mfrrRequest' list.")
    
    results = []
    
    for item in data["mfrrRequest"]:
        if item is None or not isinstance(item, dict):
            logger.warning("Skipping invalid item in data: %s", item)
            continue
        try:
            timestamp = item.get("timeStamp")
            if timestamp is None:
                logger.warning("Skipping item missing 'timeStamp': %s", item)
                continue
            mtu_start = item.get("mtuStart")
            if mtu_start is None:
                logger.warning("Skipping item missing 'mtuStart': %s", item)
                continue
            values = item.get("values")

            if values is None or not isinstance(values, list):
                logger.warning("Skipping item with invalid 'values': %s", item)
                continue

            for area in values:
                if area is None or not isinstance(area, dict):
                    logger.warning("Skipping invalid area in values: %s", area)
                    continue
                
                if "area" not in area or "value" not in area:
                    logger.warning("Skipping area missing 'area' or 'value': %s", area)
                    continue

                results.append({
                    "Time Stamp": timestamp,
                    "MTU Start": mtu_start,
                    "Area": area["area"],
                    "Value": area["value"]
                })
        except Exception as exc:
            logger.error("An error occurred while parsing data: %s", exc)
            continue


    
    return results
    