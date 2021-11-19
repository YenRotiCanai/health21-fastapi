import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate("./maptestfirebase-72508-firebase-adminsdk-hekht-06ad28a456.json")
databaseURL= "https://maptestfirebase-72508-default-rtdb.asia-southeast1.firebasedatabase.app"

firebase_admin.initialize_app(cred,{
    'databaseURL':databaseURL
})

db = firestore.client()

doc_ref = db.collection(u'users').document(u'alovelace')
doc_ref.set({
    u'first': u'Ada',
    u'last': u'Lovelace',
    u'born': 1815
})