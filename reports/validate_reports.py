import json
import os

from jsonschema import exceptions, validate


def scan_dir(dirname: str) -> list:
    subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(scan_dir(dirname))
    return subfolders


def clean_dir(dir_list: list, levels=4) -> list:
    dirs = []
    for idx, dir in enumerate(dir_list):
        if len(dir.split("/")) >= levels:
            dirs.append(dir)
    return dirs


def validate_files(output_dir: str, schema_dir: str, files: list) -> None:
    folders = clean_dir(scan_dir(output_dir))
    folders = clean_dir(folders)
    folders.sort(key=lambda x: x.replace("outputs", "").replace("/", ""))
    for folder in folders:
        for file in files:
            with open(f"{schema_dir}/schema_{file}") as json_file:
                schema = json.load(json_file)
            with open(f"{folder}/{file}") as json_file:
                data = json.load(json_file)
                try:
                    validate(data, schema)
                except exceptions.ValidationError as e:
                    print(f"error {e} {folder}/{file}")


files = [
    "1_feed_info.json",
    "2_daily_service_hours.json",
    "3_routes_changed.json",
    "3_stops_changed.json",
    "4_guideline_checks_schedule.json",
    "4_guideline_checks_rt.json",
    "5_validation_codes.json",
]

if __name__ == "__main__":
    output_dir = "outputs"
    schema_dir = "../tests/schemas"
    validate_files(output_dir, schema_dir, files)
