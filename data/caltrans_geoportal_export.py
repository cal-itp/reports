
from calitp.tables import tbl
from siuba import *
from ckanapi import RemoteCKAN
import urllib.request as urllib2
import os
import json
import requests
import pandas as pd 
from calitp import get_engine
from siuba.sql import LazyTbl

####### CONFIGURE CKAN PARAMETERS #######
API_ENDPOINT = 'https://data.ca.gov/api/3/action/resource_update'
API_Key = '46b4fbac-e6d0-4158-8dad-599d89640ec1'
####### END OF CKAN PARAMTER CONFIGURATION #######

    
agency = (
    tbl.gtfs_schedule.agency()
    >> collect()
)
df = pd.DataFrame(data=agency)
df.to_csv('gtfs_schedule_agency.csv')

#agency_csv = (
#    df = pd.DataFrame(agency)
#    df.name = agency
#    pd.DataFrame(agency).to_csv('gtfs_schedule_agency.csv')
#)

files = {'upload_file': open('gtfs_schedule_agency.csv', 'rb')}
headers = {"Content-type": "multipart/form-data",
    "Authorization" : "API_KEY",
    "id" : "e8f9d49e-2bb6-400b-b01f-28bc2e0e7df2"
} 

r = requests.post(API_ENDPOINT, files=files, headers=headers, verify = False)
print("I am response", r)

####################################

routes = (
    tbl.gtfs_schedule.routes()
    >> collect()
)
#routes_csv = [
#    df = pd.DataFrame(routes)
#    df.name = routes
#    pd.DataFrame(agency).to_csv('gtfs_schedule_routes.csv')
#]

df = pd.DataFrame(data=routes)
df.to_csv('gtfs_schedule_routes.csv')


files = {'upload_file': open('gtfs_schedule_routes.csv', 'rb')}
headers = {"Content-type": "multipart/form-data",
        "Authorization" : "API_KEY",
        "id" : "c6bbb637-988f-431c-8444-aef7277297f8"
} 

r = requests.post(API_ENDPOINT, files=files, headers=headers, verify = False)
print("I am response2", r)

####################################

stop_times = (
    tbl.gtfs_schedule.stop_times()
    >> collect()
)
df = pd.DataFrame(data=stop_times)
df.to_csv('gtfs_schedule_stop_times.csv')
#stop_times_csv = (
#    df = pd.DataFrame(stop_times)
#    df.name = stop_times
#    pd.DataFrame(stop_times).to_csv('gtfs_schedule_stop_times.csv')
#)

files = {'upload_file': open('gtfs_schedule_stop_times.csv', 'rb')}
headers = {"Content-type": "multipart/form-data",
        "Authorization" : "API_KEY",
        "id" : "d31eef2f-e223-4ca4-a86b-170acc6b2590"
} 

r = requests.post(API_ENDPOINT, files=files, headers=headers, verify = False)
print("I am response3", r)


####################################


stops = (
    tbl.gtfs_schedule.stops()
    >> collect()
)
df = pd.DataFrame(data=stops)
df.to_csv('gtfs_schedule_stops.csv')

#stops_csv = (
#    df = pd.DataFrame(stops)
#    df.name = stops
#    pd.DataFrame(stops).to_csv('gtfs_schedule_stops.csv')
#)

files = {'upload_file': open('gtfs_schedule_stops.csv', 'rb')}
headers = {"Content-type": "multipart/form-data",
        "Authorization" : "API_KEY",
        "id" : "c876204-e12b-48a2-8299-10f6ae3d4f2b"
} 

r = requests.post(API_ENDPOINT, files=files, headers=headers, verify = False)
print("I am response4", r)

####################################
trips = (
    tbl.gtfs_schedule.trips()
    >> collect()
)
df = pd.DataFrame(data=trips)
df.to_csv('gtfs_schedule_trips.csv')

#trips_csv = (
#    df = pd.DataFrame(trips)
#    df.name = trips
#    pd.DataFrame(trips).to_csv('gtfs_schedule_trips.csv')
#)

files = {'upload_file': open('gtfs_schedule_trips.csv', 'rb')}
headers = {"Content-type": "multipart/form-data",
        "Authorization" : "API_KEY",
        "id" : "0e4da89e-9330-43f8-8de9-305cb7d4918f"
} 
    
r = requests.post(API_ENDPOINT, files=files, headers=headers, verify = False)
print("I am response5", r)