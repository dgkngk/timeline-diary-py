from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List

app = FastAPI()

# MongoDB setup (assuming running locally)
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.diary



# Convert BSON ObjectId to string for JSON serialization
def entry_serializer(entry) -> dict:
    return {
        "id": str(entry["_id"]),
        "title": entry["title"],
        "writer": entry["writer"],
        "date": entry["date"],
        "text": entry["text"],
        "image": entry["image"],
    }


@app.get("/api/diary", response_model=List[DiaryEntryResponse])
async def get_diary_entries():
    entries = await db.diary.find().to_list(100)
    return [entry_serializer(entry) for entry in entries]


@app.post("/api/diary", response_model=DiaryEntryResponse)
async def create_diary_entry(entry: DiaryEntry):
    new_entry = await db.diary.insert_one(entry.dict())
    created_entry = await db.diary.find_one({"_id": new_entry.inserted_id})
    return entry_serializer(created_entry)


@app.put("/api/diary/{id}", response_model=DiaryEntryResponse)
async def update_diary_entry(id: str, updated_entry: DiaryEntry):
    entry = await db.diary.find_one({"_id": ObjectId(id)})
    if entry:
        await db.diary.update_one({"_id": ObjectId(id)}, {"$set": updated_entry.dict()})
        updated = await db.diary.find_one({"_id": ObjectId(id)})
        return entry_serializer(updated)
    raise HTTPException(status_code=404, detail="Entry not found")


@app.delete("/api/diary/{id}")
async def delete_diary_entry(id: str):
    result = await db.diary.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "Entry deleted successfully"}
    raise HTTPException(status_code=404, detail="Entry not found")
