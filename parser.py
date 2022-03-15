from bs4 import BeautifulSoup
import requests
from datetime import datetime


def holiday_parser(r):
    soup = BeautifulSoup(r.text, 'html.parser')
    holidays_table = soup.find('table', class_ = 'table table-layout-fixed')

    headers = holidays_table.find_all('thead')
    for header in headers:
        rows = header.find_all('tr')
        for row in rows:
            year_1 = row.find_all('th')[1].text.strip()
            year_2 = row.find_all('th')[2].text.strip()
            year_3 = row.find_all('th')[3].text.strip()
            print(year_1, year_2, year_3)

    holiday = []
    date_1_year = []
    date_2_year = []
    date_3_year = []

    for holidays in holidays_table.find_all('tbody'):
        rows = holidays.find_all('tr')
        for row in rows:
            holiday.append(row.find_all('td')[0].text.strip())
            try:
                date_1 = datetime.strptime(' '.join([str(elem) for elem in row.find_all('td')[1].text.strip('*').split()[1:3]])
                                           + ', ' + year_1, "%B %d, %Y").strftime("%m-%d-%Y")
            except:
                date_1 = '-'
            date_1_year.append(date_1)
            try:
                date_2 = datetime.strptime(' '.join([str(elem) for elem in row.find_all('td')[2].text.strip('*').split()[1:3]])
                                           + ', ' + year_2, "%B %d, %Y").strftime("%m-%d-%Y")
            except:
                date_2 = '-'
            date_2_year.append(date_2)
            try:
                date_3 = datetime.strptime(' '.join([str(elem) for elem in row.find_all('td')[3].text.strip('*').split()[1:3]])
                                           + ', ' + year_3, "%B %d, %Y").strftime("%m-%d-%Y")
            except:
                date_3 = '-'
            date_3_year.append(date_3)

    return list(zip(holiday, date_1_year)) + list(zip(holiday, date_2_year)) + list(zip(holiday, date_3_year))

