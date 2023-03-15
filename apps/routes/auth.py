from fastapi import APIRouter

auth = APIRouter(tags=['auth'])


@auth.get("/login")
async def root():
    return {"message": "Hello World"}


@auth.get("/register")
async def register():
    return {"message": ""}
