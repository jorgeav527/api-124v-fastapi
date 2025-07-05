from typing import Union

from fastapi import FastAPI, Depends, Form
from pymongo import MongoClient
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI()

def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    try:
        db = client["fastapi"]
        yield db
    except Exception as e:
        print(str(e))
    finally:
        client.close()

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=255)

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=255)


@app.get("/")
def index():
    return {"message": "Welcome to the API, Upgrade"}

@app.get("/post")
def get_all_post(db=Depends(get_db)):
    posts = []
    docs = db["posts"].find()
    print(docs)
    for post in docs:
        posts.append({
            "id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "created": post.get("created", datetime.now()).isoformat()
        })
    return {"total": len(posts) ,"posts": posts}


@app.post("/post/create-json-data")
def create_one_post_json_data(post: PostCreate, db = Depends(get_db)):
    new_post = {
        "title": post.title,
        "content": post.content,
        "created": datetime.now()
    }
    result = db["posts"].insert_one(new_post)
    created_post = db["posts"].find_one({"_id": result.inserted_id})

    return {
        "id": str(created_post["_id"]),
        "title": created_post["title"],
        "content": created_post["content"],
        "created": created_post["created"].isoformat()
    }

@app.post("/post/create-form-data")
def create_one_post_form_data(
    title: str = Form(..., min_length=1, max_length=20),
    content: str = Form(..., min_length=1, max_length=255),
    db=Depends(get_db)
):
    new_post = {
        "title": title,
        "content": content,
        "created": datetime.now()
    }
    result = db["posts"].insert_one(new_post)
    created_post = db["posts"].find_one({"_id": result.inserted_id})

    return {
        "id": str(created_post["_id"]),
        "title": created_post["title"],
        "content": created_post["content"],
        "created": created_post["created"].isoformat()
    }