from sqlalchemy import Column, String, Date, Integer
from database import Base


class Holidays(Base):
    __tablename__ = 'holidays'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    desc = Column(String, index=True)
    date = Column(Date, index=True)
    status = Column(String, index=True)
    sha1 = Column(String, index=True)
