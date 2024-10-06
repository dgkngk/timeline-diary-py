from pydantic import BaseModel
from typing import Optional

# Pydantic model for user registration and login
class User(BaseModel):
    username: str
    password: str

# Pydantic model for token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Token data model (used for token decoding)
class TokenData(BaseModel):
    username: Optional[str] = None


# Pydantic model for diary entries
class DiaryEntry(BaseModel):
    title: str
    writer: str
    date: str
    text: str
    image: str


class DiaryEntryResponse(DiaryEntry):
    id: str
