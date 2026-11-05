from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    """Data needed to create a user. Accepts the raw password once."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    """User data returned by the API. Never includes the password or its hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime


CalculationType = Literal["Add", "Sub", "Multiply", "Divide"]


class CalculationCreate(BaseModel):
    """Input for a new calculation. Rejects unknown types and a zero divisor."""

    a: float
    b: float
    type: CalculationType

    @model_validator(mode="after")
    def no_zero_divisor(self):
        if self.type == "Divide" and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self


class CalculationRead(BaseModel):
    """A calculation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    a: float
    b: float
    type: str
    result: float
    timestamp: datetime