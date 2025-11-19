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
from typing import Optional, Literal
from datetime import datetime

# Crypto Prediction App Schemas

class Tournament(BaseModel):
    """
    Collection name: "tournament"
    Represents a prediction tournament for a crypto asset within a time window.
    """
    title: str = Field(..., description="Display title, e.g. 'BTC 24h Sprint'")
    symbol: str = Field(..., description="Crypto symbol, e.g. BTC, ETH")
    description: Optional[str] = Field(None, description="Short description")
    prize_pool: float = Field(0, ge=0, description="Total prize pool in USDT")
    entry_fee: float = Field(0, ge=0, description="Optional entry fee in USDT")
    starts_at: datetime = Field(..., description="Start time (UTC)")
    ends_at: datetime = Field(..., description="End time (UTC)")
    status: Literal['upcoming', 'active', 'settled'] = Field('upcoming', description="Tournament status")
    result: Optional[Literal['up', 'down']] = Field(None, description="Outcome direction after settlement")

class Prediction(BaseModel):
    """
    Collection name: "prediction"
    Represents a user's prediction in a tournament.
    """
    tournament_id: str = Field(..., description="ID of the tournament")
    user_name: str = Field(..., min_length=2, max_length=40, description="Display name")
    direction: Literal['up', 'down'] = Field(..., description="Predicted direction")
    confidence: int = Field(50, ge=1, le=100, description="Confidence 1-100")

# Example legacy schemas retained for reference (not used by app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
