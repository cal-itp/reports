# Generating reports

```
docker-compose run reports /bin/bash

# inside container

. venv/bin/activate
cd app

# should produce notebooks, html and other assets in e.g. outputs/2021/05/10
make generate_parameters
make all
```
