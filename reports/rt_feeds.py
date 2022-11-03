"""
Adapted from from https://github.com/cal-itp/data-analyses/blob/8100fcd21a64fa6437ddb36701d77470b7592362/bus_service_increase/deploy_portfolio_yaml.py#L107-L129
"""
import intake
import requests
import json
from pathlib import Path
import yaml

RT_YML_URL = 'https://raw.githubusercontent.com/cal-itp/data-analyses/main/portfolio/sites/rt.yml'

# Compare the ITP IDs for parallel corridors and RT
# If URL available for RT analysis, embed in parameterized notebook
def check_if_rt_data_available():
    response = requests.get(RT_YML_URL)
    response.raise_for_status()
    analyses_data = yaml.load(response.content, yaml.Loader)

    rt_chapters = analyses_data['parts'][0]["chapters"]

    # Use a dict to capture what rank ITP ID is within that section
    # need to use it to construct URL
    rt_itp_ids_dict = {}

    for x, chapter in enumerate(rt_chapters):
        section_dict = chapter["sections"]
        for i, list_item in enumerate(section_dict):
            rt_itp_ids_dict[list_item["itp_id"]] = i

    return rt_itp_ids_dict


# failed attempt at dissecting catalog.yml to build urls for speedmaps
def get_speedmap_data():
    catalog = intake.open_catalog("./catalog.yml")
    df = catalog.competitive_route_variability.read()
    speedmap_data = []
    used = {}
    for index, district_number_and_name in enumerate(df.caltrans_district.iloc):
        if district_number_and_name is None:
            continue
        if district_number_and_name in used:
            continue
        used[district_number_and_name] = True
        district_number, name = district_number_and_name.split('-')
        speedmap_data.append([
            int(df.calitp_itp_id.iloc[index]), # calitp_id
            district_number.strip(), # district_number
            name.strip().lower().replace(' ','-'), # district_name
        ])

    return speedmap_data


# Just scrape the actual speedmap site instead
def get_speedmap_urls():
    response = requests.get('https://analysis.calitp.org/rt/README.html')
    html = response.content
    results = {}
    for line in html.decode('utf-8').split('\n'):
        if 'class="reference internal" href="district_' not in line:
            continue
        href = line.split('href="')[-1].split('"')[0]
        if 'itp_id_' not in href or '__speedmaps__district_' not in line:
            continue
        itp_id = href.split('itp_id_')[-1].split('.')[0]
        if not itp_id.isdigit():
            print(f'WARNING: skipping url because itp_id is not a number: {itp_id}')
            continue
        results[int(itp_id)] = f'https://analysis.calitp.org/rt/{href}'
    return results

if __name__ == "__main__":
    feed_dict = check_if_rt_data_available()
    with open('./outputs/rt_feed_ids.json', 'w') as f:
        f.write(json.dumps(list(feed_dict.items())))
        print('rt_feed_ids.json written')

    speedmap_urls = get_speedmap_urls()
    with open('./outputs/speedmap_urls.json', 'w') as f:
        f.write(json.dumps(list(speedmap_urls.items())))
        print('speedmap_urls.json written')