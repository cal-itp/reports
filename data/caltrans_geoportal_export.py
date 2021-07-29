
from calitp.tables import tbl
from siuba import *
from ckanapi import RemoteCKAN
import urllib.request as urllib2
import os
import json
import requests

from calitp import get_engine
from siuba.sql import LazyTbl

####### CONFIGURE CKAN PARAMETERS #######
API_ENDPOINT = "https://data.ca.gov/api/3/action/resource_update"
API_Key = os.environment.get('46b4fbac-e6d0-4158-8dad-599d89640ec1')
#"46b4fbac-e6d0-4158-8dad-599d89640ec1"
####### END OF CKAN PARAMTER CONFIGURATION #######

files = {'upload_file': open('file.csv','rb')}
headers= {'Content-Type': "multipart/form-data", 
                 "Authorization": 'API_KEY',
                 'resource_id_dictionary'
} # this is a dict 

r = requests.post(API_ENDPOINT, files=files, headers=headers)




resource_id_dictionary =
{'id' : [
    'e8f9d49e-2bb6-400b-b01f-28bc2e0e7df2', #agency
    'c6bbb637-988f-431c-8444-aef7277297f8', #routes
    'd31eef2f-e223-4ca4-a86b-170acc6b2590', #stop_times
    'c876204-e12b-48a2-8299-10f6ae3d4f2b', #stops 
    '0e4da89e-9330-43f8-8de9-305cb7d4918f' #trips
     ]
}
    
]
print()



########RESOURCE IDS #########
AGENCY = e8f9d49e-2bb6-400b-b01f-28bc2e0e7df2
ROUTES = c6bbb637-988f-431c-8444-aef7277297f8
STOP_TIMES = d31eef2f-e223-4ca4-a86b-170acc6b2590
STOPS = 8c876204-e12b-48a2-8299-10f6ae3d4f2b
TRIPS = 0e4da89e-9330-43f8-8de9-305cb7d4918f


tbl_gtfs_schedule_agency = (
    tbl_gtfs_schedule.agency() >> collect
)
tbl_gtfs_schedule_routes = (
    tbl_gtfs_schedule.routes() >> collect
)
tbl_gtfs_schedule_stop_times = (
    tbl_gtfs_schedule.stop_times() >> collect
)
tbl_gtfs_schedule_stops = (
    tbl_gtfs_schedule.stops() >> collect
)
tbl_gtfs_schedule_trips = (
    tbl_gtfs_schedule.trips() >> collect
)

#agency
files = {'upload_file': open('file.csv', 'rb')}
headers = {'Content-type: "multipart/form-data",
        "Authorization" : 'API_KEY',
        "id: e8f9d49e-2bb6-400b-b01f-28bc2e0e7df2"
}
#routes
files = {'upload_file': open('file.csv', 'rb')}
headers = {'Content-type: "multipart/form-data",
        "Authorization" : 'API_KEY',
        "id: c6bbb637-988f-431c-8444-aef7277297f8"
}
#stop_times 
files = {'upload_file': open('file.csv', 'rb')}
headers = {'Content-type: "multipart/form-data",
        "Authorization" : 'API_KEY',
        "id: d31eef2f-e223-4ca4-a86b-170acc6b2590"
}
#stops
files = {'upload_file': open('file.csv', 'rb')}
headers = {'Content-type: "multipart/form-data",
        "Authorization" : 'API_KEY',
        "id: 8c876204-e12b-48a2-8299-10f6ae3d4f2b"
}
#trips
files = {'upload_file': open('file.csv', 'rb')}
headers = {'Content-type: "multipart/form-data",
        "Authorization" : 'API_KEY',
        "id: 0e4da89e-9330-43f8-8de9-305cb7d4918f"
}


# cycle through and do a put request for each 
#routes
#stop times
#stops