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

event_no = 1 # 梯次
event_name = "event " + str(event_no)
# regArea = '香山'
# regRouteNum = 3
# regSheetID = '02e12lkfdgu4032958430qehkjhk432kjkjh'

def set_sheet(regArea, regRouteNum, regSheetUrl, routes):
    sheet_ref = db.collection('sheet_Info').document(event_name).collection('area').document(regArea)
    # sheet_ref = db.collection(u'sheet_Info').document('event1')
    sheet_ref.set({
        'routeNum': regRouteNum,
        'sheetUrl': regSheetUrl,
        'routes' : json.dumps(routes)
    })

# set_sheet(regArea,regRouteNum,regSheetID)

def get_sheet(regArea):
    sheet_ref = db.collection('sheet_Info').document(event_name).collection('area').document(regArea)
    doc = sheet_ref.get()
    doc_data = doc.to_dict()
    # doc_JSON = json.dumps(doc_data)
    # print(doc_data)
    return doc_data

def get_mapArea():
    docs_ref = db.collection('sheet_Info').document(event_name).collection('area')
    docs = docs_ref.stream()
    # for doc in docs:
    #     print(f'{doc.id} => {doc.to_dict()}')

    doc_dict = {}
    for doc in docs:
        doc_dict[doc.id] = doc.to_dict()

    # print(doc_dict)

    return doc_dict

# get_mapArea()