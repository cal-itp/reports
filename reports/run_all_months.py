# A helper script that executes all necessary commands to generate reports for multiple
# year and month combinations

import multiprocessing
import subprocess

# use 1.5x the amount of CPUs for processing since there are times when CPU usage is low
# due to network requests taking a while
parellelization = int(multiprocessing.cpu_count() * 1.5)
report_months = [{
  'year': 2021,
  'months': [5, 6, 7, 8, 9, 10, 11]
}]

# generate the IDs
subprocess.run(['make generate_parameters'], check=True, shell=True)

# read original Makefile contents
with open('Makefile', 'r') as f:
  originalContents = f.readlines()

def rewriteMakefileForYearAndMonth(year, month):
  newlines = originalContents.copy()
  if month < 10:
    month = f"0{month}"

  newlines[1] = f"NOTEBOOKS=$(subst parameters.json,index.html,$(wildcard outputs/{year}/{month}/*/parameters.json))"
  with open('Makefile', 'w') as f:
    f.writelines(newlines)


# iterate through each year and month combo to generate reports
for year in report_months:
  for month in year['months']:
    rewriteMakefileForYearAndMonth(year['year'], month)
    
    subprocess.run([f"make all -j {parellelization}"], check=True, shell=True)

# rewrite original Makefile
with open('Makefile', 'w') as f:
    f.writelines(originalContents)