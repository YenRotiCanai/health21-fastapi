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

# 處理csv
df = pd.read_csv('test_data.csv', index_col='身份證') #以身份證號碼當 index
df_dict = df.to_dict(orient='index')

df_restaurant = pd.read_csv('test_data - 餐廳.csv', index_col='序號')
df_contestant = pd.read_csv('test_data - 最終參賽者名單2.csv', index_col='身份證')

rest_dict = df_restaurant.to_dict(orient='index')
cont_dict = df_contestant.to_dict(orient='index')

routes_list_test =  [[0, 1, 7, 4, 11, 3, 10, 0], [0, 5, 15, 16, 6, 2, 0], [0, 12, 13, 9, 14, 8, 0]]

ref = db.reference('/')

event_no = 1
event_name = "event" + str(event_no)
startDate = "20211101"
endDate = "20211121"

# 更新/新增路線
def update_routes(routes_list):
    route_ref = ref.child('routes')

    for i, route in enumerate(routes_list_test):
        route_ref.update({
            i:{
                "order" : json.dumps(route)
            }
        })

# update_routes(routes_list_test)

# 更新/新增餐廳
def update_restaurant(rest_dict):
    rest_ref = db.reference("/"+event_name+"/restaurants/")
    rest_ref.update(rest_dict)

# update_restaurant(rest_dict)

# 更新/新增參賽者
def update_contestant(cont_dict):
    cont_ref = db.reference("/"+event_name+"/contestant/")
    cont_ref.update(cont_dict)

# update_contestant(cont_dict)

def get_deliveryRequest():
    cont_ref = db.reference("/"+event_name+"/contestant/")
    # query = cont_ref.order_by_child('運費').equal_to("外送").get()
    snapshot = cont_ref.order_by_key().equal_to("取餐方式").equal_to("外送").get()
    print(type(snapshot))
    print(snapshot)

get_deliveryRequest()