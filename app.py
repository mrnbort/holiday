from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import schemas
from datetime import date
import requests
from parser import holiday_parser
from db_fill import holiday_db
import hashlib


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Holidays).order_by(models.Holidays.date.asc()).all()


@app.post('/holidays/')
async def reload_holidays(  # user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)):
    db.query(models.Holidays).order_by(models.Holidays.date.asc()).all()
    url = 'https://www.nyse.com/markets/hours-calendars'
    resp = requests.get(url)
    holidays_tuple = holiday_parser(resp)
    for holiday in holidays_tuple:
        holiday_db(db, holiday)

    return successful_response(200)


@app.post("/")
async def create_holiday(holiday: schemas.HolidayCreate,
                         # user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    # if user is None:
    #     raise get_user_exception()
    holiday_model = models.Holidays()
    holiday_model.desc = holiday.desc
    holiday_model.date = holiday.date
    holiday_model.status = 'modified'
    holiday_model.sha1 = hashlib.sha1((holiday.desc+str(holiday.date)).encode('utf-8')).hexdigest()

    db.add(holiday_model)
    db.query(models.Holidays).order_by(models.Holidays.date.asc()).all()
    db.commit()

    return successful_response(201)


@app.put("/{holiday_date}")
async def update_holiday(holiday_date: date,
                         holiday: schemas.HolidayUpdate,
                         # user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    # if user is None:
    #     raise get_user_exception()

    holiday_model = db.query(models.Holidays) \
        .filter(models.Holidays.date == holiday_date) \
        .first()

    if holiday_model is None:
        raise http_exception()

    holiday_model.desc = holiday.desc
    holiday_model.status = 'modified'

    db.add(holiday_model)
    db.commit()

    return successful_response(200)


@app.delete("/{holiday_date}")
async def delete_holiday(holiday_date: date,
                         # user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    # if user is None:
    #     raise get_user_exception()

    if db.query(models.Holidays) \
            .filter(models.Holidays.date == holiday_date) is None:
        raise http_exception()

    db.query(models.Holidays).filter(models.Holidays.date == holiday_date).update({models.Holidays.status: 'deleted'})

    db.commit()

    return successful_response(200)


@app.delete("/holidays_delete/")
async def delete_holidays(holiday_date_start: date,
                          holiday_date_end: date,
                          # user: dict = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    # if user is None:
    #     raise get_user_exception()

    if db.query(models.Holidays) \
            .filter(models.Holidays.date >= holiday_date_start)\
            .filter(models.Holidays.date <= holiday_date_end) is None:
        raise http_exception()

    db.query(models.Holidays).filter(models.Holidays.date >= holiday_date_start, models.Holidays.date <=
                                     holiday_date_end).update({models.Holidays.status: 'deleted'})

    db.commit()

    return successful_response(200)


def http_exception():
    return HTTPException(status_code=404, detail="Holiday not found")


def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }
# uvicorn app:app --reload
