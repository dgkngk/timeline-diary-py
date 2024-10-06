from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from motor.motor_asyncio import AsyncIOMotorClient
from jose import JWTError, jwt
from .auth_utils import verify_password, get_password_hash, create_access_token, decode_access_token
from .models import User, Token, TokenData
from .constants import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

app = FastAPI()

# MongoDB setup (assuming MongoDB is running locally)
client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client.diary  # Use a 'diary' database

# OAuth2PasswordBearer: Token will be passed in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User registration endpoint
@app.post("/register")
async def register(user: User):
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    user_data = {"username": user.username, "password": hashed_password}
    await db.users.insert_one(user_data)
    return {"message": "User registered successfully"}

# Login and generate a JWT token
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency to get the current user from a token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    username = decode_access_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Protected route, only accessible with a valid token
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
