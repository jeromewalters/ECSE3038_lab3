from fastapi import FastAPI, Request, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
import motor.motor_asyncio
import pydantic
from datetime import datetime
from pydantic import BaseModel


api = FastAPI()

allowed_origins = [
    "https://ecse3038-lab3-tester.netlify.app", "http://localhost:8000"
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://jeromewalters:devilswag@cluster0.bbcfvve.mongodb.net/?retryWrites=true&w=majority",tls=True, tlsAllowInvalidCertificates=True)

database = conn.tank_system

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

@api.get("/profile")
async def get_user_profile():
    user_profile = await database["profile"].find().to_list(999)
    if len(user_profile) < 1:
        return {}
    return user_profile[0]


@api.post("/profile", status_code=201)
async def create_profile(request: Request):
    profile_data = await request.json()
    profile_data["last_updated"] = datetime.now()

    new_profile = await database["profile"].insert_one(profile_data)
    created_profile = await database["profile"].find_one({"_id": new_profile.inserted_id})

    return created_profile


@api.post("/data", status_code=201)
async def create_tank(request: Request):
    tank_data = await request.json()

    new_tank = await database["tank"].insert_one(tank_data)
    created_tank = await database["tank"].find_one({"_id": new_tank.inserted_id})
    return created_tank


@api.get("/data")
async def retrieve_tanks():
    tanks = await database["tank"].find().to_list(999)
    return tanks


@api.patch("/data/{id}")
async def update_tank(id: str, request: Request):
    update_data = await request.json()
    updated_tank = await database["tank"].update_one({"_id": ObjectId(id)}, {'$set': update_data})
    
    if updated_tank.modified_count == 1:
        current_tank = await database["tank"].find_one({"_id": id})
        if current_tank is not None:
            return current_tank   
    else:
        raise HTTPException(status_code=404, detail="Item was not found")


@api.delete("/data/{id}")
async def do_delete(id:str):
    deleted_tank = await database["tank"].delete_one({"_id": ObjectId(id)})
    
    if deleted_tank.deleted_count == 1:
        return {"message": "Tank deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Item was not found")