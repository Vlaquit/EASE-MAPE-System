import datetime
import time

import pymongo
from numpy import mean


def main():
    mongo_client = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
    db = mongo_client.monitoring
    db.cpu_data.drop()
    while True:
        last_data_items = list(db.containers.find(sort=[('_id', pymongo.DESCENDING)]).limit(5))
        liste = []
        for dict in last_data_items:
            dict = list(dict.items())
            for i in range(2, len(dict) - 1):
                liste.append(dict[i][1].get("cpu").get("cpu_usage"))
                print(dict[i][1].get("cpu").get("cpu_usage"))
        average_cpu = mean(liste)
        db.cpu_data.insert({'date': datetime.datetime.utcnow(), "cpu_average": average_cpu})
        time.sleep(8)


if __name__ == "__main__":
    main()
