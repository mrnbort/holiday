import sqlite3


def holiday_db(holidays_tuple):

    conn = sqlite3.connect('holidays.db')
    c = conn.cursor()

    c.execute('''DROP TABLE IF EXISTS holidays''')
    c.execute('''CREATE TABLE holidays(holiday TEXT, date TEXT)''')
    c.executemany('''INSERT INTO holidays VALUES(?, ?)''', holidays_tuple)
    print('We have inserted', c.rowcount, 'records to the table.')
    conn.commit()
    c.execute('''SELECT * FROM holidays''')
    results = c.fetchall()
    print(results)
    conn.close()

# update insert if does not exist
