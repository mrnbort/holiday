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
