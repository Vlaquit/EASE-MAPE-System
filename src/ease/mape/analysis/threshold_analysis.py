import os
import time

import pymongo
from dotenv import load_dotenv

# Get environment variable
load_dotenv()

client = pymongo.MongoClient("mongodb+srv://" + os.getenv("MONGODB_ID") + ":" + os.getenv("MONGODB_PW") + "@cluster0-wuhr3.mongodb.net/test?retryWrites=true&w=majority")
db = client.monitoring


def analyse_cpu(value):
    if value > float(os.getenv("CPU_UPPER_THRESHOLD")):
        return 1
    elif value < float(os.getenv("CPU_LOWER_THRESHOLD")):
        return 2
    else:
        return 0


def get_data():
    while True:
        last_data = db.containers_data.find_one(sort=[('_id', pymongo.DESCENDING)])
        only_containers_data = list(last_data.items())
        for i in range(2, len(only_containers_data)):
            print(only_containers_data[i][1].get("cpu").get("cpu_usage"))
            print("Result: {} \n".format(analyse_cpu(only_containers_data[i][1].get("cpu").get("cpu_usage"))))
        time.sleep(5)


if __name__ == '__main__':
    get_data()
