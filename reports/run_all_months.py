# A helper script that executes all necessary commands to generate reports for multiple
# year and month combinations

from pathlib import Path

import multiprocessing
import subprocess

# use 1.5x the amount of CPUs for processing since there are times when CPU usage is low
# due to network requests taking a while
parellelization = int(multiprocessing.cpu_count() * 1.5)
report_months = [{
  'year': 2021,
  'months': [5, 6, 7, 8, 9, 10, 11, 12]
},{
  'year': 2022,
  'months': [1, 2]
}
]
print(report_months)

# generate the IDs
subprocess.run(['make generate_parameters'], check=True, shell=True)

# iterate through each year and month combo to create make arguments
make_arguments = []
for year in report_months:
  for month in year['months']:
    if month < 10:
        month = f'0{month}'
    year_month_dirs = list(Path("outputs").glob(f"{year['year']}/{month}/*"))
    year_month_args = [ymd / "index.html" for ymd in year_month_dirs]
    make_arguments = [*make_arguments, *year_month_args]

# run all arguments
subprocess.check_output(['make', '-j', str(parellelization), *make_arguments])