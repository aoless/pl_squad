from typing import List

from pydantic import BaseModel, Field


class Player(BaseModel):
    firstname: str = Field(..., description="Player’s first name")
    lastname: str = Field(..., description="Player’s last name")
    age: int = Field(..., description="Player’s age")
    number: int = Field(..., description="Player’s number")
    birth_date: str = Field(..., description="YYYY‑MM‑DD")
    birth_place: str = Field(..., description="Player’s birth place")
    position: str = Field(..., description="Primary playing position")
    photo: str = Field(..., description="URL to player’s photo")


class Squad(BaseModel):
    players: List[Player]
