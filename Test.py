# import pymongo
# import sys
# try:
#   client = pymongo.MongoClient("mongodb+srv://cisegaf375:VamTDJKa11DGxntI@cluster0.yom51.mongodb.net/Users?retryWrites=true&w=majority&appName=Cluster0")

# except pymongo.errors.ConfigurationError:
#   print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
#   sys.exit(1)

# db = client.myDatabase

# my_collection = db["recipes"]

# recipe_documents = [{ "name": "elotes", "ingredients": ["corn", "mayonnaise", "cotija cheese", "sour cream", "lime"], "prep_time": 35 },
#                     { "name": "loco moco", "ingredients": ["ground beef", "butter", "onion", "egg", "bread bun", "mushrooms"], "prep_time": 54 },
#                     { "name": "patatas bravas", "ingredients": ["potato", "tomato", "olive oil", "onion", "garlic", "paprika"], "prep_time": 80 },
#                     { "name": "fried rice", "ingredients": ["rice", "soy sauce", "egg", "onion", "pea", "carrot", "sesame oil"], "prep_time": 40 }]
# my_collection.insert_many(recipe_documents)

# for recipe in my_collection.find():
#     print(recipe)


import jwt

token = jwt.decode("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3OTcyMWMzM2NiMTlkYWMxYzE1NTE1NCIsImVtYWlsIjoidXNlcjNAZ21haWwuY29tIiwidXNlcm5hbWUiOiJ1c2VyMyIsImV4cCI6MTczNzk4NjQxMn0.4zsh4svHdMZ0PtxcFpnaNiwlmiG-jGD8dFCvf-wk_Wo", "django-insecure-&^s#@(-h_(1z_=qp1p4fp%m+01fz84arn3cv791ol49sume5lv", algorithms=["HS256"])
print(token)