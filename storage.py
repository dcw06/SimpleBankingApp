import json
import os
from typing import Optional

from bank import Bank

def get_data_dir() -> str:
    """Get the app data directory, creating it if needed."""
    data_dir = os.path.expanduser("~/.SimpleBankingApp")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_data_file() -> str:
    """Get the full path to bank_data.json in the app data directory."""
    return os.path.join(get_data_dir(), "bank_data.json")


def save_bank(bank: Bank, filename: Optional[str] = None) -> None:
    if filename is None:
        filename = get_data_file()
    with open(filename, "w") as f:
        json.dump(bank.to_dict(), f, indent=2)


def load_bank(filename: Optional[str] = None) -> Bank:
    if filename is None:
        filename = get_data_file()
    if not os.path.exists(filename):
        return Bank()
    with open(filename) as f:
        data = json.load(f)
    return Bank.from_dict(data)
