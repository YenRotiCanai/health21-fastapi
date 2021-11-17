from fastapi import FastAPI, UploadFile, File

import requests
import json
import urllib.request as ur
from urllib.parse import quote
import string

import ortools
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

import pandas as pd

app = FastAPI()

@app.get("/")
def hello():
    return {"message":"hihi"}