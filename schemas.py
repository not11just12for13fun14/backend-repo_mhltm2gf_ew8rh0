"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# Event schema -> collection name: "event"
class Event(BaseModel):
    title: str = Field(..., description="Event title")
    date: datetime = Field(..., description="Event start datetime (ISO)")
    venue: str = Field(..., description="Venue name")
    city: Optional[str] = Field(None, description="City")
    description: Optional[str] = Field(None, description="Short description")
    image: Optional[str] = Field(None, description="Cover image URL")
    tags: Optional[List[str]] = Field(default=None, description="Event tags")
    price: Optional[float] = Field(default=0.0, ge=0, description="Ticket price")

# Ticket schema -> collection name: "ticket"
class Ticket(BaseModel):
    event_id: str = Field(..., description="Related event id as string")
    name: str = Field(..., description="Attendee full name")
    email: EmailStr = Field(..., description="Attendee email")
    quantity: int = Field(default=1, ge=1, le=10, description="Number of tickets")

# Example schemas kept for reference (not used by the app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
