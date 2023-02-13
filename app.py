from fastapi import FastAPI, Request, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
import motor.motor_asyncio
import pydantic
from datetime import datetime
from pydantic import BaseModel



app = FastAPI()

origins = [
    
    "https://ecse3038-lab3-tester.netlify.app", "http://localhost:8000"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://jeromewalters:jeromewalters@cluster0.bbcfvve.mongodb.net/?retryWrites=true&w=majority",tls=True, tlsAllowInvalidCertificates=True)

db = client.tank_system

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

@app.get("/profile")
async def get_profile():
    profile = await db["profile"].find().to_list(999)
    if len(profile) < 1:
        return {}
    return profile[0]



@app.post("/profile",status_code=201)
async def newprofile(request:Request):
    
    Objprofile = await request.json()
    Objprofile["last_updated"]=datetime.now()

    new_profile = await db["profile"].insert_one(Objprofile)
    created_profile = await db["profile"].find_one({"_id": new_profile.inserted_id})

    return created_profile




@app.post("/data",status_code=201)
async def newprofile(request:Request):
    ObjTank = await request.json()

    new_tank = await db["tank"].insert_one(ObjTank)
    customtank = await db["tank"].find_one({"_id": new_tank.inserted_id})
    return customtank

    
@app.get("/data")
async def retrive_tanks():
    tanks = await db["tank"].find().to_list(999)
    return tanks

    

@app.patch("/data/{id}")
async def do_update(id:str, request: Request):
    updated= await request.json()
    updated_tank = await db["tank"].update_one({"_id":ObjectId(id)}, {'$set': updated})
    
    if updated_tank.modified_count == 1:
         if (
                current_tank := await db["tank"].find_one({"_id": id})
            ) is not None:
                return current_tank   
    else:
         raise HTTPException(status_code=404, detail="Item was not found")


@app.delete("/data/{id}",status_code=204)
async def delete_tank(id: str):

    tank_deleter= await db["tank"].find_one({"_id": ObjectId(id)})
    erase_tank= await db["tank"].delete_one({"_id":ObjectId(id)})