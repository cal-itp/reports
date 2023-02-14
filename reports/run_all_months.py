# A helper script that executes all necessary commands to generate reports for multiple
# year and month combinations

import multiprocessing
import subprocess
from datetime import datetime

# use 1.5x the amount of CPUs for processing since there are times when CPU usage is low
# due to network requests taking a while
parellelization = int(multiprocessing.cpu_count() * 1.5)
current_month = datetime.now().strftime("%m")
# get the months from the current calendar year
year_months = [i for i in range(1, int(current_month) + 1)]
report_months = [
    # Reports go back to June, 2022.
    {"year": 2022, "months": [6, 7, 8, 9, 10, 11, 12]},
    {"year": 2023, "months": year_months},
]

# generate the IDs
subprocess.run(["make generate_parameters"], check=True, shell=True)

# iterate through each year and month combo to create make arguments
make_arguments = []
for year_dict in report_months:
    for month in year_dict["months"]:
        if month < 10:
            month = f"0{month}"
        make_arguments = (
            f"make YEAR={year_dict['year']} MONTH={month} all -j {parellelization}"
        )
        subprocess.run(make_arguments, check=True, shell=True)
