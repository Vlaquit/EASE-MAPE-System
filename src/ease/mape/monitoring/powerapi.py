import csv
import pymongo

mongo_client = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
db = mongo_client.monitoring
collection = db.rapl_out
cursor = collection.find({})

with open('powerapi.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(["date", "power"])

with open('powerapi.csv', 'a') as f:
    writer = csv.writer(f)
    for document in cursor:
        writer.writerow([document['timestamp'].strftime('%H:%M:%S'), document['power']])
