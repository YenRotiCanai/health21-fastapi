from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from io import StringIO

import json
import pandas as pd

from routing import main_routing
from sheet import main_sheet2df, route2df, routeListSheet2json
from firestore_db import set_sheet, get_sheet

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class sheetInfo(BaseModel):
    area: str
    routeNum: int
    sheetUrl: str


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
    routes = main_routing(df) # call main function
    return routes

@app.post("/regSheet/")
def regSheet(sheet: sheetInfo):

    area = sheet.area
    routeNum = sheet.routeNum
    sheetUrl = sheet.sheetUrl

    # 登錄資料到 firebase 上面
    set_sheet(area, routeNum, sheetUrl)
    
    # 自動計算經緯度和距離後，新增一個工作表來放
    # 最後回傳一個 dataframe
    df = main_sheet2df(sheetUrl)
    
    # # 呼叫路線分組 func，回傳路線的 list
    routes = main_routing(df, routeNum)

    # # 把路線變成 dataframe 存到新的工作表
    route2df(df, routes, sheetUrl)

    return{
        "area":area,
        "routeNum":routeNum,
        "sheetUrl":sheetUrl,
        "routesJson":json.dumps(routes)
    }

@app.get("/getSheet/{mapArea}")
def getSheet(mapArea):
    gs = get_sheet(mapArea)
    print(gs['regSheetID'])
    routesJson = routeListSheet2json(gs['regSheetID'])
    print(routesJson)
    # gs_JSON = json.dumps(gs)
    return{
        "area":mapArea,
        "routeNum":gs['regRouteNum'],
        "sheetUrl":gs['regSheetID'],
        "routesJson": routesJson
    }

