import json
import os

CONFIG_PATH = ".config/config.json"


def read_directory():
    if not os.path.exists(CONFIG_PATH):
        return ""

    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)

    return data.get("last_directory", "")


def save_directory(path):
    os.makedirs(".config", exist_ok=True)

    data = {
        "last_directory": path
    }

    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)