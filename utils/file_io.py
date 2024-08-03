import json


def read_json(file_path: str) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)


def write_to_json(file_path: str, data: dict):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
