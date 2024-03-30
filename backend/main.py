from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, constr
from pymongo import MongoClient

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["user_registration"]
collection = db["users"]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allow specific methods
    allow_headers=["*"],  # Allow all headers
)

# Define Pydantic model for user data
class User(BaseModel):
    username: str
    password: constr(min_length=6)
    confirmPassword: constr(min_length=6)  # Confirm password field
    email: EmailStr
    phoneNumber: constr(min_length=11, max_length=11)

# Route for user registration
@app.post("/register")
async def register_user(user: User):
    # Check if username already exists
    if collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    if collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Check if phone number already exists
    if collection.find_one({"phoneNumber": user.phoneNumber}):
        raise HTTPException(status_code=400, detail="Phone number already exists")
    
    # Check if password matches confirm password
    if user.password != user.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Save user data to MongoDB
    collection.insert_one(user.dict())
    return {"message": "User registered successfully"}

# Route to echo back received JSON data
@app.post("/")
async def main(request: Request):
    data = await request.json()
    print("Received JSON data:", data)
    return ""
