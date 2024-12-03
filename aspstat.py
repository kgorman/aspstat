import requests
import os
import time
from requests.auth import HTTPDigestAuth
import argparse

ATLAS_USER = os.environ["ATLAS_USER"]
ATLAS_USER_KEY = os.environ["ATLAS_USER_KEY"]
BASE_URL = "https://cloud.mongodb.com/api/atlas/v2/"
HEADERS = {
    'Accept': 'application/vnd.atlas.2024-05-30+json',
    'Content-Type': 'application/json'
}
AUTH = HTTPDigestAuth(ATLAS_USER, ATLAS_USER_KEY)
SECONDS = 5

def get_stats(group, instance, processor):
    """ get stats for an stream processor """
    url = "groups/{}/streams/{}/processor/{}".format(group, instance, processor)
    response = requests.get(BASE_URL+url, auth=AUTH, headers=HEADERS)
    return response.json()

def get_processors(group, instance):
    """ get all processors for the instance """
    url = "groups/{}/streams/{}/processors".format(group, instance)
    response = requests.get(BASE_URL+url, auth=AUTH, headers=HEADERS)
    return response.json()['results']

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--group', type=str, required=True, help='The project ID')
    parser.add_argument('--instance', type=str, required=True, help='The instance name')
    args = parser.parse_args()
    g = args.group
    i = args.instance

    imc = 0
    ims = 0
    omc = 0
    oms = 0

    iter = 0 

    # output formatting, padding
    header_template = "{:<12} {:<12} {:<12} {:<12} {:<12}"
    data_template = "{:<12} {:<12} {:<12} {:<12} {:<12}"

    while True:

        # header row, every 5 outputs
        if iter % 5 == 0:
            print(header_template.format("PC", "IMC", "IMS", "OMS", "OMC"))
        iter += 1

        # data rows
        pc = 0
        for processor in get_processors(g, i):
            pc += 1
            s = get_stats(g, i, processor['name'])
            imc = round((imc+s['stats']['inputMessageCount'])/SECONDS, 0)
            ims = round((ims+s['stats']['inputMessageSize'])/SECONDS, 0)
            oms = round((oms+s['stats']['outputMessageSize'])/SECONDS, 0)
            omc = round((omc+s['stats']['outputMessageCount'])/SECONDS, 0)
        print(data_template.format(pc, imc, ims, oms, omc))
        time.sleep(SECONDS)

if __name__ == "__main__":
    main()
