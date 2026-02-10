from data_processing import process_event

raw = {
    "transaction_id": "TX_1",
    "customer_id": "CUST_1",
    "timestamp": "2024-09-30T00:00:01Z",
    "amount": 10,
    "currency": "eur",
    "country": "fr",
    "merchant_category": "GAMING",
    "velocity_last_hour": {"num_transactions": 2, "total_amount": 25}
}

print(process_event(raw))