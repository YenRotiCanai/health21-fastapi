from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from io import StringIO

import json
import pandas as pd

from routing import main

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello():
    return {"message":"hihi"}

# 吃網站上傳的 csv 進來
@app.post("/uploadfile/")
async def create_file(file: UploadFile = File(...)):
    content = await file.read()
    content2 = content.decode('utf-8') #更改csv編碼

    """start ortools routing"""
    routes = str2df(content2) #取得路線routes as list
    routes_json = json.dumps(routes) #以json格式回傳路線給網站
    
    return {
        "filename" : file.filename,
        "routes" : routes_json
    }

def str2df(data):
    df = pd.read_csv(StringIO(data))
    # print(type(df))
    print(df.head())
    # d = create_data(df)
    # print(d)
    routes = main(df) # call main function
    return routes



