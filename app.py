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
from auth import get_validation_status

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_nyse_url():
    return 'https://www.nyse.com/markets/hours-calendars'


@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Holidays).order_by(models.Holidays.date.asc()).all()


@app.get("/list_holidays/")
async def list_holidays_for_a_date_range(holiday_date_start: date,
                                         holiday_date_end: date,
                                         db: Session = Depends(get_db)):
    holiday_list = db.query(models.Holidays).filter(models.Holidays.date >= holiday_date_start,
                                                    models.Holidays.date <= holiday_date_end)\
                                            .filter(models.Holidays.status != 'deleted')\
                                            .with_entities(models.Holidays.desc, models.Holidays.date)\
                                            .order_by(models.Holidays.date.asc()).all()
    if len(holiday_list) == 0:
        raise http_exception()

    return holiday_list


@app.get("/is_holiday/")
async def is_holiday(date_to_check: date,
                     db: Session = Depends(get_db)):
    if db.query(models.Holidays).filter(models.Holidays.date == date_to_check).first() is None:
        return "Not a holiday."
    else:
        return "Is a holiday."


@app.post('/holidays/')
async def reload_holidays(validation: bool = Depends(get_validation_status),
                          db: Session = Depends(get_db), url: str = Depends(get_nyse_url)):
    if not validation:
        return

    db.query(models.Holidays).order_by(models.Holidays.date.asc()).all()
    resp = requests.get(url)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="source refused to provide data")

    holidays_tuple = holiday_parser(resp)
    for holiday in holidays_tuple:
        holiday_db(db, holiday)

    return {"loaded": len(holidays_tuple)}


@app.post("/")
async def create_holiday(holiday: schemas.HolidayCreate,
                         validation: bool = Depends(get_validation_status),
                         db: Session = Depends(get_db)):
    if validation is True:
        holiday_model = models.Holidays()
        holiday_model.desc = holiday.desc
        holiday_model.date = holiday.date
        holiday_model.status = 'modified'
        holiday_model.sha1 = hashlib.sha1((holiday.desc + str(holiday.date)).encode('utf-8')).hexdigest()

        db.add(holiday_model)
        db.query(models.Holidays).order_by(models.Holidays.date.asc()).all()
        db.commit()

        return successful_response(201)


@app.put("/{holiday_date}")
async def update_holiday(holiday_date: date,
                         holiday: schemas.HolidayUpdate,
                         validation: bool = Depends(get_validation_status),
                         db: Session = Depends(get_db)):
    if validation is True:

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
                         validation: bool = Depends(get_validation_status),
                         db: Session = Depends(get_db)):
    if validation is True:

        if db.query(models.Holidays) \
                .filter(models.Holidays.date == holiday_date).first() is None:
            raise http_exception()

        db.query(models.Holidays).filter(models.Holidays.date == holiday_date).update({models.Holidays.status: 'deleted'})

        db.commit()

        return successful_response(200)


@app.delete("/holidays_delete/")
async def delete_holidays(holiday_date_start: date,
                          holiday_date_end: date,
                          validation: bool = Depends(get_validation_status),
                          db: Session = Depends(get_db)):
    if validation is True:

        if db.query(models.Holidays) \
                .filter(models.Holidays.date >= holiday_date_start) \
                .filter(models.Holidays.date <= holiday_date_end).first() is None:
            raise http_exception()

        db.query(models.Holidays).filter(models.Holidays.date >= holiday_date_start, models.Holidays.date <=
                                         holiday_date_end).update({models.Holidays.status: 'deleted'})

        db.commit()

        return successful_response(200)


def http_exception():
    return HTTPException(status_code=404, detail="No holidays found.")


def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }

# uvicorn app:app --reload
