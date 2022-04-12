import models
from sqlalchemy.orm import Session
import hashlib


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
