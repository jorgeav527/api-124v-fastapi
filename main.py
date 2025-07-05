from typing import Optional

from fastapi import FastAPI, Depends, Form, HTTPException, Path, Query, Header
from pymongo import MongoClient
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

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

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=255)


@app.get("/")
def index():
    return {"message": "Welcome to the API, Upgrade"}

# @app.get("/post")
# def get_all_post(db=Depends(get_db)):
#     posts = []
#     docs = db["posts"].find()
#     for post in docs:
#         posts.append({
#             "id": str(post["_id"]),
#             "title": post["title"],
#             "content": post["content"],
#             "created": post.get("created", datetime.now()).isoformat()
#         })
#     return {"total": len(posts) ,"posts": posts}


@app.get("/posts")
def buscar_posts(
    titulo: Optional[str] = Query(None, min_length=1, max_length=255, description="Filtrar por título"),
    db = Depends(get_db)
):
    filtro = {}
    if titulo:
        filtro["title"] = {"$regex": titulo, "$options": "i"}

    docs = db["posts"].find(filtro)

    posts = []
    for post in docs:
        posts.append({
            "id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "created": post.get("created", datetime.now()).isoformat()
        })
    return {"total": len(posts) ,"posts": posts}


@app.get("/post/{post_id}")
def obtener_post(
    post_id: str = Path(...,
                       title="ID del post",
                       description="ID del post a obtener",
                       min_length=24,
                       max_length=24,
                       regex="^[0-9a-fA-F]{24}$"),
    db = Depends(get_db)
):
    try:
        post = db["posts"].find_one({"_id": ObjectId(post_id)})

        if not post:
            return {"error": "post no encontrado"}

        return {
            "id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "created": post["created"].isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


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


@app.get("/posts/secure/")
def obtener_posts_secure(
    authorization: str = Header(..., alias="Authorization", description="Token en formato 'Bearer <token>'"),
    db=Depends(get_db)
):
    if not authorization.startswith("Bearer "):
        return {"error": "Formato de token inválido. Use 'Bearer <token>'"}
    
    token = authorization[7:]
    if token != "secreto123":
        return {"error": "No es el <token>'"}
    
    docs = db["posts"].find({})

    posts = []
    for post in docs:
        posts.append({
            "id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "created": post.get("created", datetime.now()).isoformat()
        })
    return {"total": len(posts) ,"posts": posts}