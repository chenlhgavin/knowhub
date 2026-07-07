"""Solution 04: JSON and CSV

Practice serializing and deserializing data with JSON and CSV formats:
- Saving and loading JSON files
- Writing and reading CSV files using csv.DictWriter / csv.DictReader
- Round-trip data integrity
"""

import csv
import json


def save_json(data: dict, filepath: str) -> None:
    """Save a dictionary as a formatted JSON file.

    The JSON should be human-readable with 2-space indentation
    and written in UTF-8 encoding.

    Args:
        data: The dictionary to serialize.
        filepath: Path to the output JSON file.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(filepath: str) -> dict:
    """Load a dictionary from a JSON file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        The deserialized dictionary.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def records_to_csv(records: list[dict], filepath: str) -> None:
    """Write a list of dictionaries as a CSV file.

    Uses csv.DictWriter. The fieldnames (column headers) are taken
    from the keys of the first record.

    Args:
        records: A list of dicts with consistent keys.
        filepath: Path to the output CSV file.
    """
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def csv_to_records(filepath: str) -> list[dict]:
    """Read a CSV file into a list of dictionaries.

    Uses csv.DictReader. Each row becomes a dict mapping
    column headers to values.

    Args:
        filepath: Path to the CSV file.

    Returns:
        A list of dicts, one per row.
    """
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


if __name__ == "__main__":
    import tempfile
    import os

    # --- JSON round-trip ---
    data = {
        "name": "Alice",
        "age": 30,
        "scores": [95, 87, 92],
        "active": True,
        "address": {
            "city": "Wonderland",
            "zip": "12345",
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                     delete=False) as tmp:
        tmp_path = tmp.name

    try:
        save_json(data, tmp_path)
        loaded = load_json(tmp_path)
        assert loaded == data

        # Verify it is formatted (has newlines, not a single line)
        with open(tmp_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "\n" in content
        assert "  " in content  # Indentation present
    finally:
        os.unlink(tmp_path)

    # --- CSV round-trip ---
    records = [
        {"name": "Alice", "age": "30", "city": "Wonderland"},
        {"name": "Bob", "age": "25", "city": "Builderland"},
        {"name": "Charlie", "age": "35", "city": "Chocolate Factory"},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv",
                                     delete=False) as tmp:
        tmp_path = tmp.name

    try:
        records_to_csv(records, tmp_path)
        loaded = csv_to_records(tmp_path)
        assert loaded == records

        # Verify structure
        assert len(loaded) == 3
        assert loaded[0]["name"] == "Alice"
        assert loaded[2]["city"] == "Chocolate Factory"
    finally:
        os.unlink(tmp_path)

    # --- JSON with empty dict ---
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                     delete=False) as tmp:
        tmp_path = tmp.name

    try:
        save_json({}, tmp_path)
        loaded = load_json(tmp_path)
        assert loaded == {}
    finally:
        os.unlink(tmp_path)

    # --- CSV single record ---
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv",
                                     delete=False) as tmp:
        tmp_path = tmp.name

    try:
        single = [{"x": "1", "y": "2"}]
        records_to_csv(single, tmp_path)
        loaded = csv_to_records(tmp_path)
        assert loaded == single
    finally:
        os.unlink(tmp_path)

    print("All sol04_json_csv tests passed!")
