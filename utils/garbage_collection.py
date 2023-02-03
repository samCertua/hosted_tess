import datetime
import time

def garbage_collection(d: dict):
    while True:
        print(d)
        to_delete = []
        for k,v in d.items():
            if (datetime.datetime.now()-v["last_active"]).seconds>300:
                to_delete.append(k)
        for t in to_delete:
            del d[t]
        time.sleep(600)