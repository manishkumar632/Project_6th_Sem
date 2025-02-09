import pymongo
import sys
from decouple import config
try:
    # Fetch URI and database name from settings

    # Initialize MongoDB client
    client = pymongo.MongoClient(config('MONGODB_URI'))

    # Access the database
    db = client['Readoxy']
    print("Connected to MongoDB successfully!")

except KeyError as e:
    print(f"Missing key in MONGO_DB settings: {e}")
    sys.exit(1)
except pymongo.errors.ConfigurationError as e:
    print(f"An Invalid URI host error occurred: {e}")
    sys.exit(1)
