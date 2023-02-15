import json
import os
import sys

from jsonschema import validate

sys.path.append(os.path.abspath("../reports"))
from generate_reports_data import generate_data_by_file_path
from validate_reports import validate_files

test_file = "outputs/2022/11/91/1_file_info.json"

# Instead of unit tests, this generates a test output directory, then validates
# the data.
print(f"generating {test_file}")
# generate_data_by_file_path(test_file)

files = [
    "1_feed_info.json",
    "2_daily_service_hours.json",
    "3_routes_changed.json",
    "3_stops_changed.json",
    "4_file_check.json",
    "5_validation_codes.json",
]
output_dir = "outputs/2022/11/91"
schema_dir = "schemas"
validate_files(output_dir, schema_dir, files)
