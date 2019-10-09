import csv
import datetime
import io
import json
import time

import pytz
import requests

url = "http://localhost:1936/;csv"


def get_haproxy_stats(url):
    req = requests.get(url, auth=("root", "password"))
    page = req.content
    data = page.decode("utf8")
    # print(data)
    reader = csv.DictReader(io.StringIO(data))
    json_data = json.dumps(list(reader))
    # print(json_data)
    return json_data


def get_response_time(json_data):
    rtime = json.loads(json_data)[4].get("ttime")
    session_rate = json.loads(json_data)[4].get("rate")
    cur_session = json.loads(json_data)[4].get("scur")

    return [rtime, session_rate, cur_session]


if __name__ == "__main__":
    with open('rtime.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "rtime", "session_rate", "scur"])
    while True:
        time.sleep(1)
        liste = [datetime.datetime.now(pytz.timezone('America/Montreal')).strftime('%H:%M:%S')] + get_response_time(get_haproxy_stats(url))
        print(liste)
        with open('rtime.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(liste)
