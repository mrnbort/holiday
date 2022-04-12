from pydantic import BaseModel
from datetime import date


class HolidayCreate(BaseModel):
    desc: str
    date: date

    class Config:
        orm_mode = True


class HolidayUpdate(BaseModel):
    desc: str

    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str

    class Config:
        orm_mode = True


class VerifyUser(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True
