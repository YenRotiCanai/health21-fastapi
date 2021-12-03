import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import pandas as pd
import json

# Use a service account
cred = credentials.Certificate("./credentials2.json")
databaseURL= "https://maptestfirebase-72508-default-rtdb.asia-southeast1.firebasedatabase.app"

firebase_admin.initialize_app(cred,{
    'databaseURL':databaseURL
})

db = firestore.client()

#--- test ---#
# doc_ref = db.collection(u'users').document(u'alovelace')
# doc_ref.set({
#     u'first': u'Ada',
#     u'last': u'Lovelace',
#     u'born': 1815
# })
#------------#

df_restaurant = pd.read_csv('test_data - 餐廳.csv', index_col='序號')
df_contestant = pd.read_csv('test_data - 最終參賽者名單2.csv', index_col='身份證')

routes_list_test =  [[0, 1, 7, 4, 11, 3, 10, 0], [0, 5, 15, 16, 6, 2, 0], [0, 12, 13, 9, 14, 8, 0]]


rest_dict = df_restaurant.to_dict(orient='index')
cont_dict = df_contestant.to_dict(orient='index')

event_no = 1
event_name = "event" + str(event_no)
startDate = "20211101"
endDate = "20211121"

def set_cont(cont_dict):
    doc_cont_ref = db.collection(event_name).document(u'contestants')
    doc_cont_ref.set(cont_dict)

def set_routes(routes):
    route_dict = {}
    doc_route_ref = db.collection(event_name).document(u'routes')
    
    for i, r in enumerate(routes):
        route_name = "route" + str(i)
        route_dict[route_name] = str(r)

    print(route_dict)
    doc_route_ref.set(route_dict)

def set_rest(rest_dict):
    doc_rest_ref = db.collection(event_name).document(u'restaurants')
    doc_rest_ref.set(rest_dict)

# set_cont(cont_dict)
# set_rest(rest_dict)
set_routes(routes_list_test)

