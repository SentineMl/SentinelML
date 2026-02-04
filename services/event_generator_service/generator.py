import json 
import os 
import random 
import uuid
import time 
import datetime
from datetime import timezone 

# Config via env vars (good practice)
SLEEP_SECONDS = float(os.getenv("SLEEP_SECONDS", "1.0"))
ANOMALY_RATE = float(os.getenv("ANOMALY_RATE", "0.05"))  # 5% anomalies by default


MERCHANTS=["Amazon","Walmart","Target","BestBuy","Ebay","Costco","HomeDepot","Nike","Adidas","Starbucks","McDonalds"]
COUNTRY1=["US","UK","FR","DE","CN","CA","AU","TN"]
COUNTRY2=["IN","JP","BR","NG"]
USERS=[f"user_{i:04d}" for i in range(1, 201)]
def gen_normal_event():
    transaction_id= f"{uuid.uuid4().hex}"
    user_id = random.choice(USERS)
    amount=round(random.uniform(5,300),2)
    country = random.choice(COUNTRY1)
    timestamp = datetime.now(timezone.utc).isoformat()
    merchant= random.choice(MERCHANTS) 
    currency=random.choice(["USD","EUR"])
    return({
        "event_type":"transaction",
        "transaction_id":transaction_id,
        "user_id":user_id,
        "amount":amount,
        "country":country,
        "timestamp":timestamp,
        "merchant":merchant,
        "currency":currency,
        "label":0,
        })
def gen_anomaly_event():
    anomaly_type = random.choice(["high_amount", "country_change", "burst_like"])
    base=gen_normal_event()
    base["label"]=1
    base["anomaly_type"] = anomaly_type

    if anomaly_type=="high_amount":
        base["amount"]=round(random.uniform(1000,5000),2)
    elif anomaly_type=="country_change":
        base["country"]=random.choice(COUNTRY2)
    elif anomaly_type=="burst_like":
        base["burst_hint"]=True
        base["amount"]=round(random.uniform(200,1000),2)
    return base

def main():
    random.seed()
    
    while True:
        is_anomaly = random.random()<ANOMALY_RATE
        event = gen_anomaly_event() if is_anomaly else gen_normal_event()

        print(json.dumps(event))
        time.sleep(SLEEP_SECONDS)

if __name__=="__main__":
    main()