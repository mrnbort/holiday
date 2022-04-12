from database import engine, session
import models
from sqlalchemy.orm import Session
from models import Holidays
import schemas
import hashlib

# models.Base.metadata.create_all(engine)


def holiday_db(db: Session, holiday):
    db_item = models.Holidays()
    db_item.desc = holiday[0]
    db_item.date = holiday[1]
    db_item.status = 'loaded'
    db_item.sha1 = hashlib.sha1((holiday[0]+str(holiday[1])).encode('utf-8')).hexdigest()
    if db.query(models.Holidays) \
            .filter(models.Holidays.sha1 == db_item.sha1).first() is None:
        db.add(db_item)
        db.commit()
        return 'A new holiday added'
    else:
        return 'Unique constraint violation'


# def holiday_db(holidays_tuple):
#     for holiday in holidays_tuple:
#         add_holi = Holidays(desc=holiday[0], date=holiday[1])
#         if session.query(models.Holidays) \
#                 .filter(models.Holidays.desc == holiday[0]) \
#                 .filter(models.Holidays.date == holiday[1]).first() is None:
#             session.add(add_holi)
#             session.commit()
#             print('A new holiday added')
#         else:
#             print('Unique constraint violation')
#     session.close()
