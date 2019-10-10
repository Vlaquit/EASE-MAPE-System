import csv
import datetime
import io
import json
import time

import pytz
import requests
from numpy import mean

url = "http://localhost:1936/;csv"


def get_haproxy_stats(url):
    req = requests.get(url, auth=("root", "password"))
    page = req.content
    data = page.decode("utf8")
    reader = csv.DictReader(io.StringIO(data))
    data = json.dumps(list(reader))
    return data


def get_data(data):
    rtime_list = []
    session_rate_list = []
    cur_session_list = []
    for stat in json.loads(data):
        if "web" in stat.get("svname") and stat.get("status") == "UP":
            rtime_list.append(int(stat.get("rtime")))
            session_rate_list.append(int(stat.get("rate")))
            cur_session_list.append(int(stat.get("scur")))
            # print(stat)

    return [round(mean(rtime_list), 2), round(mean(session_rate_list), 2), round(mean(cur_session_list), 2)]

# if __name__ == "__main__":
#     with open('rtime.csv', 'w') as f:
#          writer = csv.writer(f)
#          writer.writerow(["Date", "rtime", "session_rate", "scur"])
#     while True:
#          time.sleep(5)
#          liste = [datetime.datetime.now(pytz.timezone('America/Montreal')).strftime('%H:%M:%S')] + get_data(get_haproxy_stats(url))
#          print(liste)
#          with open('rtime.csv', 'a') as f:
#              writer = csv.writer(f)
#              writer.writerow(liste)
