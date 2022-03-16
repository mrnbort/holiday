from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.exc import IntegrityError


SQLALCHEMY_DATABASE_URL = "sqlite:///./holidays.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Session = sessionmaker()
Base = declarative_base()
Session.configure(bind=engine)
session = Session()


class Holidays(Base):
    __tablename__ = 'holidays'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    holiday = Column(String, index=True)
    date = Column(DateTime, unique=True)


Base.metadata.create_all(engine)


def holiday_db(holidays_tuple):
    for holiday in holidays_tuple:
        add_holi = Holidays(holiday=holiday[0], date=holiday[1])
        try:
            session.add(add_holi)
            session.commit()
            print('A new holiday added')
        except IntegrityError:
            session.rollback()
            print('Unique constraint violation')
    session.close()
