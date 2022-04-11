from bs4 import BeautifulSoup
from datetime import datetime


def holiday_parser(r):
    try:
        soup = BeautifulSoup(r.text, 'html.parser')
    except AttributeError:
        soup = BeautifulSoup(r, 'html.parser')
    holidays_table = soup.find('table', class_='table table-layout-fixed')

    years = []

    headers = holidays_table.find_all('thead')
    for header in headers:
        rows = header.find_all('tr')
        for row in rows:
            years.append(row.find_all('th')[1].text.strip())
            years.append(row.find_all('th')[2].text.strip())
            years.append(row.find_all('th')[3].text.strip())

    holiday = []
    date_year = []

    date_extraction = lambda x, y: datetime.strptime(' '.join([str(elem) for elem in row.find_all('td')[x].text
                                                              .strip('*').split()[1:3]]) + ', ' + y, "%B %d, %Y").date()

    for holidays in holidays_table.find_all('tbody'):
        rows = holidays.find_all('tr')
        for year in range(len(years)):
            for row in rows:
                try:
                    date = date_extraction(year + 1, years[year])
                    date_year.append(date)
                    holiday.append(row.find_all('td')[0].text.strip())
                except ValueError:
                    pass

    return list(zip(holiday, date_year))
