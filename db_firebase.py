import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import json
import pandas as pd

cred = credentials.Certificate("./maptestfirebase-72508-firebase-adminsdk-hekht-06ad28a456.json")
databaseURL= "https://maptestfirebase-72508-default-rtdb.asia-southeast1.firebasedatabase.app"

firebase_admin.initialize_app(cred,{
    'databaseURL':databaseURL
})

df = pd.read_csv('/test_data.csv')

routes_list_test =  [[0, 1, 7, 4, 11, 3, 10, 0], [0, 5, 15, 16, 6, 2, 0], [0, 12, 13, 9, 14, 8, 0]]

ref = db.reference('/')

event_no = 1
startDate = "20211101"
endDate = "20211121"
contestant = {
    "IC" : "A0123456789",
    "Name" : "Mr.Apple",
    "Phone" : "097812345678",
    "PickUpAddr" : "300 Hsinchu Train Station"
}

ctjson = json.dumps(contestant)

ref.update({
    "event":{
        "no" : event_no,
        "startDate" : startDate,
        "endDate" : endDate,
        "contestant" : {
            contestant
        }
    }
})

# event_ref = db.reference('/event_no/')
# event = event_ref.get()
# print(event)

def update_routes(routes_list):
    route_ref = ref.child('routes')

    for i, route in enumerate(routes_list_test):
        route_ref.update({
            i:{
                "order" : json.dumps(route)
            }
        })

# 更新/新增路線
# update_routes(routes_list_test)