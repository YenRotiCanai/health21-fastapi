from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/")
def hello():
    return {"message":"hihi"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {
        "filename" : file.filename
    }