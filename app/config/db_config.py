import pymongo

ENV = "qa"

# def get_db():
if ENV == "qa":
    client = pymongo.MongoClient(
        "mongodb+srv://novacept:QdH3bIChIEMyDXBr@panrange-cluster.wkfg1lx.mongodb.net/?retryWrites=true&w=majority")
elif ENV == "dev":
    client = pymongo.MongoClient("mongodb://localhost:27017")

db = client.DigiMachine  # Example database name

