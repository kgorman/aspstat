import requests
import os
import time
from requests.auth import HTTPDigestAuth
import argparse
import pprint

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
    dlq = 0     # dlq count
    ss = 0      # state size
    fc = 0
    optime = 0

    iter = 0 

    # output formatting, padding
    header_template = "{:<4} {:<4} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}"
    data_template = "{:<4} {:<4} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}"

    while True:

        # header row, every 5 outputs
        if iter % 10 == 0:
            print(header_template.format("Proc", "Fail", "Input Count", "Input Size", "Output Count", "Output Size", "DLQ", "State Size", "opTime"))
        iter += 1

        # data rows, divide by seconds gives per second metrics
        pc = 0
        optime = 0
        for processor in get_processors(g, i):
            pc += 1
            s = get_stats(g, i, processor['name'])
            imc = round((imc+s['stats']['inputMessageCount'])/SECONDS, 0)
            ims = round((ims+s['stats']['inputMessageSize'])/SECONDS, 0)
            oms = round((oms+s['stats']['outputMessageSize'])/SECONDS, 0)
            omc = round((omc+s['stats']['outputMessageCount'])/SECONDS, 0)
            dlq = round((dlq+s['stats']['dlqMessageCount'])/SECONDS, 0)
            ss = round((ss+s['stats']['stateSize'])/SECONDS, 0)
            if s['state'] == 'FAILED':
                fc += 1
            for ii in s['stats']['operatorStats']:
                optime += ii['timeSpentMillis']
        print(data_template.format(pc, fc, imc, ims, omc, oms, dlq, ss, optime))
        time.sleep(SECONDS)

if __name__ == "__main__":
    main()
