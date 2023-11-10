from flask import Flask, render_template, request, jsonify
from bson.objectid import ObjectId
import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from pprint import pprint
import urllib.parse

app = Flask(__name__)

# Set up the MongoDB connection by retrieving username / password and host from env
#username = urllib.parse.quote_plus(os.environ['MONGO_USER'])
#password = urllib.parse.quote_plus(os.environ['MONGO_PWD'])
#mongohost = os.environ['MONGO_HOST']
client = MongoClient("mongodb://john:password@localhost:27017/")  # Replace with your MongoDB connection string
db = client["user_database"]
usr_coll = db["user_collection"]
subs_coll = db["user_subscription"]
plan_coll = db["pricing_plan"]
indexes = usr_coll.list_indexes()
index_found = False
for idx in indexes:
    if "first_name_1_last_name_1" == idx["name"]:
        index_found = True
        break

if not index_found:
   usr_coll.create_index([("first_name", DESCENDING), ("last_name", ASCENDING)], name="first_name_1_last_name_1", unique=True)
   pprint("created first_name_1_last_name_1 index")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/remove', methods=['DELETE'])
def remove_user():
    filter = {}
    if not (request.form.get('first_name') is None):
        filter['first_name'] = request.form['first_name']
    if not (request.form.get('last_name') is None):
        filter['last_name'] = request.form['last_name']
    if len(filter) == 0:
        return "must specify first_name or last_name", 400
    result = usr_coll.delete_many(filter)
    return "deleted " + str(result.deleted_count) + " records"

@app.route('/user/query', methods=['GET'])
def query():
    result = list()
    filter = {}
    if not (request.args.get('first_name') is None):
        filter['first_name'] = request.args['first_name']
    if not (request.args.get('last_name') is None):
        filter['last_name'] = request.args['last_name']
    if not (request.args.get('_id') is None):
        filter['_id'] = ObjectId(request.args['_id'])
    result = list(usr_coll.find(filter))
    if (len(result) == 0):
        return "Not found", 400
    ans = ""
    for item in result:
        ans += str(item)
    return ans

def check_plan_id():
    return

@app.route('/user/submit', methods=['POST'])
def user_submit():
    filter = {}
    if not request.form.get('planid') is None:
        filter['id'] = request.form.get('planid')
        result = list(plan_coll.find(filter))
        if (len(result) == 0):
            return "plan id not found", 400
    elif not request.form.get('isactive') is None:
        return "cannot activate without plan", 400

    data = {
        "first_name": request.form.get('first_name'),
        "middle_name": request.form.get('middle_name'),
        "last_name": request.form.get('last_name'),
        "phone": request.form.get('phone'),
        "second_phone": request.form.get('second_phone'),
        "email": request.form.get('email'),
        "verified": request.form.get('verified'),
        "address": request.form.get('address'),
        # field profile_image marks the start of settings
        "profile_image": request.form.get('profile_image'),
        "languages": request.form.get('languages'),
        "industries": request.form.get('industries'),
        "occupations": request.form.get('occupations'),
        "is_dark_mode": request.form.get('is_dark_mode'),
        "bio": request.form.get('bio'),
        # field planid marks the start of subscription
        "planid": request.form.get('planid'),
        "isactive": request.form.get('isactive'),
    }

    try:
        with client.start_session() as ses:
            ses.start_transaction()
            # Insert the data into MongoDB
            usr_coll.insert_one(data)
            ses.commit_transaction()
    except DuplicateKeyError:
        return "record with same key exists\n", 400
    except ConnectionFailure:
        return "cannot connect to server", 500

    return "Data submitted successfully."

@app.route('/user/update', methods=['PUT'])
def user_update():
    filter = {}
    if not request.form.get('planid') is None:
        filter['id'] = request.form.get('planid')
        result = list(plan_coll.find(filter))
        if (len(result) == 0):
            return "plan id not found", 400
    elif not request.form.get('isactive') is None:
        return "cannot activate without plan", 400

    if request.form.get('first_name') is None:
        return "must specify first_name", 400

    if request.form.get('last_name') is None:
        return "must specify last_name", 400
    data = {
        "middle_name": request.form.get('middle_name'),
        "phone": request.form.get('phone'),
        "second_phone": request.form.get('second_phone'),
        "email": request.form.get('email'),
        "verified": request.form.get('verified'),
        "address": request.form.get('address'),
        # field profile_image marks the start of settings
        "profile_image": request.form.get('profile_image'),
        "languages": request.form.get('languages'),
        "industries": request.form.get('industries'),
        "occupations": request.form.get('occupations'),
        "is_dark_mode": request.form.get('is_dark_mode'),
        "bio": request.form.get('bio'),
        # field planid marks the start of subscription
        "planid": request.form.get('planid'),
        "isactive": request.form.get('isactive'),
    }

    try:
        with client.start_session() as ses:
            ses.start_transaction()
            # Insert the data into MongoDB
            usr_coll.update_one({'first_name': request.form.get('first_name'),
                                 'last_name': request.form.get('last_name')},
                                 {"$set": data}, upsert=False)
            ses.commit_transaction()
    except DuplicateKeyError:
        return "record with same key exists\n", 400
    except ConnectionFailure:
        return "cannot connect to server", 500

    return "Data submitted successfully."

@app.route('/pricing_plan/remove', methods=['DELETE'])
def remove_plan():
    filter = {}
    if (request.form.get('id') is None):
        return "must specify plan id", 400
    filter['planid'] = request.form.get('id')
    result = list(usr_coll.find(filter))
    if (len(result) > 0):
        return "plan id still in use", 400
    filter = {}
    filter['id'] = request.form.get('id')
    result = plan_coll.delete_one(filter)
    return "deleted " + str(result.deleted_count) + " plan records"

@app.route('/pricing_plan/submit', methods=['POST'])
def pricing_submit():
    filter = {}
    filter['id'] = request.form.get('id')
    result = list(plan_coll.find(filter))
    if (len(result) > 0):
        return "plan id exists", 400
    data = {
        "name": request.form.get('name'),
        "id": request.form.get('id'),
        "term": request.form.get('term'),
        "rate": request.form.get('rate'),
        "description": request.form.get('description'),
    }
    try:
        with client.start_session() as ses:
            ses.start_transaction()
            # Insert the data into MongoDB
            plan_coll.insert_one(data)
            ses.commit_transaction()
    except DuplicateKeyError:
        return "record with same key exists\n", 400
    except ConnectionFailure:
        return "cannot connect to server", 500

    return "Data submitted successfully."

if __name__ == '__main__':
    app.run(debug=True)
