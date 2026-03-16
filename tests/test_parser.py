import pytest
from app.parser import clean_data

correct_data = {
    "mfrrRequest": [
    {
      "timeStamp": "2026-03-15T17:15:01+00:00",
      "mtuStart": "2026-03-15T17:30:00+00:00",
      "values": [
        {"area": "DK1","value": 145.0},
        {"area": "DK2","value": 75.0}]
    }]
}

def test_clean_data_datatype():
    with pytest.raises(ValueError, match="Data is empty or None."):
        clean_data(None)
        
    with pytest.raises(ValueError, match="Data is empty or None."):
        clean_data({})

    with pytest.raises(ValueError, match="Invalid input data: expected a payload with an 'mfrrRequest' list."):
        clean_data({"invalidKey": []})

    with pytest.raises(ValueError, match="Invalid input data: expected a payload with an 'mfrrRequest' list."):
        clean_data({"mfrrRequest": "not a list"})

    result = clean_data({"mfrrRequest": []})
    assert result == []

def test_clean_data_correct_data():
    result = clean_data(correct_data)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["Area"] == "DK1"
    assert result[0]["Value"] == 145.0
    assert result[1]["Area"] == "DK2"
    assert result[1]["Value"] == 75.0


def test_clean_data_skips_item_missing_timestamp():
    result = clean_data({
        "mfrrRequest": [
            {
                "timeStamp": None,
                "mtuStart": "2026-03-15T17:30:00+00:00",
                "values": [
                    {"area": "DK1", "value": 145.0},
                    {"area": "DK2", "value": 75.0}
                ]
            }
        ]
    })

    assert result == []

def test_clean_data_skips_item_missing_mtuStart():
    result = clean_data({
        "mfrrRequest": [
            {
                "timeStamp": "2026-03-15T17:15:01+00:00",
                "mtuStart": None,
                "values": [
                    {"area": "DK1", "value": 145.0},
                    {"area": "DK2", "value": 75.0}
                ]
            }
        ]
    })
    assert result == []

def test_clean_data_skips_item_missing_values():
    result = clean_data({
        "mfrrRequest": [
            {
                "timeStamp": "2026-03-15T17:15:01+00:00",
                "mtuStart": "2026-03-15T17:30:00+00:00",
                "values": None
            }
        ]
    })
    result2 = clean_data({
        "mfrrRequest": [
            {
                "timeStamp": "2026-03-15T17:15:01+00:00",
                "mtuStart": "2026-03-15T17:30:00+00:00",
                "values": "Not a list"
            }
        ]
    })
    result3 = clean_data({
        "mfrrRequest": [
            {
                "timeStamp": "2026-03-15T17:15:01+00:00",
                "mtuStart": "2026-03-15T17:30:00+00:00",
                "values": [None, "Not a dict", {"area": "DK1"}]
            }
        ]
    })

    assert result == []
    assert result2 == []
    assert result3 == []

def test_clean_data_skips_invalid_area_entries():
    result = clean_data({
        "mfrrRequest": [
            {
                "timeStamp": "2026-03-15T17:15:01+00:00",
                "mtuStart": "2026-03-15T17:30:00+00:00",
                "values": [
                    None,
                    {"area": "DK1", "value": 145.0},
                ]
            }
        ]
    })

    result2 = clean_data({
        "mfrrRequest": [
            {
                "timeStamp": "2026-03-15T17:15:01+00:00",
                "mtuStart": "2026-03-15T17:30:00+00:00",
                "values": [
                    {"area": "DK1"},
                    {"value": 75.0},
                    {"area": "DK2", "value": 50.0}
                ]
            }
        ]
    })

    assert len(result) == 1
    assert result[0]["Area"] == "DK1"
    assert result[0]["Value"] == 145.0
    assert len(result2) == 1
    assert result2[0]["Area"] == "DK2"
    assert result2[0]["Value"] == 50.0
    




