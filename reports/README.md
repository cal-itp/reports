# Generating reports

```
docker-compose run reports /bin/bash

# inside container

. venv/bin/activate
cd app

# should produce notebooks, html and other assets in e.g. outputs/2021/05/10
# replace -j 8 with the number of notebooks to build in parallel
# the build process is not computationally intensive, but requires waiting on 
# http requests to google bigquery
make generate_parameters
make all -j 8
```

Finally, to push report data to the production bucket, run the following.

```
# NOTE: currently need to replace gtfs-data-test with gtfs-data in Makefile
# to push to production
make sync
```
