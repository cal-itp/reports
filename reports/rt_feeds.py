"""
Adapted from from https://github.com/cal-itp/data-analyses/blob/8100fcd21a64fa6437ddb36701d77470b7592362/bus_service_increase/deploy_portfolio_yaml.py#L107-L129
"""
import yaml
import json

from pathlib import Path

# Compare the ITP IDs for parallel corridors and RT
# If URL available for RT analysis, embed in parameterized notebook
def check_if_rt_data_available(portfolio_site_yaml: Path) -> dict:
    with open(portfolio_site_yaml) as analyses:
        analyses_data = yaml.load(analyses, yaml.Loader)

    rt_chapters = analyses_data['parts'][0]["chapters"]

    # Use a dict to capture what rank ITP ID is within that section
    # need to use it to construct URL
    rt_itp_ids_dict = {}

    for x, chapter in enumerate(rt_chapters):
        section_dict = chapter["sections"]
        for i, list_item in enumerate(section_dict):
            rt_itp_ids_dict[list_item["itp_id"]] = i

    return rt_itp_ids_dict



if __name__ == "__main__":
    import sys
    feed_dict = check_if_rt_data_available(sys.argv[1])
    with open('./outputs/rt_feed_ids.json', 'w') as f:
        f.write(json.dumps(list(feed_dict.keys())))
        print('rt_feed_ids.json written')