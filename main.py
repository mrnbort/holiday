import requests

from parser import holiday_parser
from database import holiday_db

url = 'https://www.nyse.com/markets/hours-calendars'

resp = requests.get(url)
holidays_tuple = holiday_parser(resp)
holiday_db(holidays_tuple)

