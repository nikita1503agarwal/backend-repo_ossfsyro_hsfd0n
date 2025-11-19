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

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# App-specific schemas for Krishna GPT

class Message(BaseModel):
    """
    Messages collection schema
    Collection name: "message"
    """
    role: str = Field(..., description="'user' or 'krishna' to identify speaker")
    content: str = Field(..., description="Message text content")
    image_url: Optional[str] = Field(None, description="Optional image accompanying the message")
    conversation_id: Optional[str] = Field(None, description="Conversation/thread identifier")

class Conversation(BaseModel):
    """
    Conversation collection schema
    Collection name: "conversation"
    """
    title: str = Field(..., description="Conversation title or first question snippet")
    participant: Optional[str] = Field("Arjuna", description="User name, defaults to Arjuna")
    last_activity: Optional[datetime] = Field(default=None, description="Timestamp of last message")
    message_ids: Optional[List[str]] = Field(default=None, description="IDs of messages in this conversation")

# Example schemas (kept for reference)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
