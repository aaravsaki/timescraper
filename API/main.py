from fastapi import FastAPI
import queries


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/empty")
async def empty_rooms():
    return queries.empty_rooms()
