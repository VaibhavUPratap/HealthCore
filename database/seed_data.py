# seed_data.py placeholder
# scripts/seed_csv.py
import os, csv
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()
uri = os.environ.get("MONGO_URI")
if not uri:
    raise RuntimeError("MONGO_URI not found in .env")

client = MongoClient(uri)
dbname = os.environ.get("MONGO_DBNAME") or client.get_default_database().name or "healthcore"
db = client[dbname]
coll = db["datasets"]

csv_path = "models/water_quality_master.csv"  # change if different

if not os.path.exists(csv_path):
    raise FileNotFoundError(f"{csv_path} not found. Update path in script.")

with open(csv_path, newline="", encoding="utf8") as f:
    reader = csv.DictReader(f)
    batch = []
    for i, row in enumerate(reader, start=1):
        # try convert numeric fields
        for k in ["cases","turbidity","ph","chlorine","lat","lng"]:
            if k in row and row[k] != "":
                try:
                    row[k] = float(row[k]) if "." in row[k] else int(row[k])
                except:
                    pass
        row["created_at"] = datetime.utcnow()
        batch.append(row)
        if i % 500 == 0:
            coll.insert_many(batch)
            batch = []
    if batch:
        coll.insert_many(batch)

print("Seeding complete. Documents in datasets:", coll.count_documents({}))
