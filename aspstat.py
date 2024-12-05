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
    """Get stats for a stream processor."""
    url = "groups/{}/streams/{}/processor/{}".format(
        group, instance, processor)
    try:
        response = requests.get(BASE_URL + url, auth=AUTH, headers=HEADERS)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stats: {e}")
        return None


def get_processors(group, instance):
    """Get all processors for the instance."""
    url = "groups/{}/streams/{}/processors".format(group, instance)
    try:
        response = requests.get(BASE_URL + url, auth=AUTH, headers=HEADERS)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        if 'results' in data:
            return data['results']
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching processors: {e}")
        return []

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
    fc = 0      # failed count
    optime = 0  # sum of all operator times
    kidle = 0   # kafka idle partitions
    lag = 0     # kafka lag
    iter = 0

    # output formatting, padding
    header_template = "{:<4} {:<4} {:<12} {:<12} {:<12} {:<12} {:<6} {:<12} {:<6} {:<6} {:<6}"
    data_template = "{:<4} {:<4} {:<12} {:<12} {:<12} {:<12} {:<6} {:<12} {:<6} {:<6} {:<6}"

    while True:

        pc = 0
        optime = 0
        Pimc = imc
        imc = 0
        Pims = ims
        ims = 0
        Pomc = omc
        omc = 0
        Poms = oms
        oms = 0
        Pss = ss
        ss = 0

        for processor in get_processors(g, i):
            # get the stats for the processor
            s = get_stats(g, i, processor['name'])
            
            # compute stats that are cumulative and return per second
            imc = imc+s['stats']['inputMessageCount']
            ims = ims+s['stats']['inputMessageSize']
            oms = oms+s['stats']['outputMessageSize']
            omc = omc+s['stats']['outputMessageCount']
            dlq = dlq+s['stats']['dlqMessageCount']
            ss = ss+s['stats']['stateSize']

            # all other stats
            if s['state'] == 'STARTED':
                pc += 1
            if s['state'] == 'FAILED':
                fc += 1
            for ii in s['stats']['operatorStats']:
                optime += ii['timeSpentMillis']
            if 'kafkaPartitions' in s['stats']:
                for ii in s['stats']['kafkaPartitions']:
                    if ii['isIdle']:
                        kidle += 1
            if 'kafkaTotalOffsetLag' in s:
                lag = lag+s['stats']['kafkaTotalOffsetLag']

        # header row, every 5 outputs
        if iter % 10 == 0:
            print(header_template.format("Proc", "Fail", "Input Count", "Input Size",
                  "Output Count", "Output Size", "DLQ", "State Size", "opTime", "kIdle", "kLag"))
        if iter != 0: 
            print(data_template.format(pc, fc, int(imc-Pimc), int(ims-Pims), int(omc-Pomc), int(oms-Poms), dlq, int(ss-Pss), optime, kidle, lag))
        iter += 1
        time.sleep(SECONDS)

if __name__ == "__main__":
    main()
