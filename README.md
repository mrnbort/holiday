# Holiday service [![Run Tests and Build an Image](https://github.com/mrnbort/holiday/actions/workflows/ci.yml/badge.svg)](https://github.com/mrnbort/holiday/actions/workflows/ci.yml)

## Description

Holiday service is a service that provides information on all U.S. holidays observed by NYSE markets.
The service pulls the list of holidays from NYSE website on a daily basis.
Any user can check if a specific date is a holiday and get a list of all holidays for a specific date range.
It also allows the admin user to update and add a holiday record. 
In addition, the admin can also remove a holiday record or holiday records for a specific date range.

## Run in Docker

1. Copy docker-compose.yml
    
    - change the ports if needed
    - for nginx service, change `volumes` to your service config

2. Create or copy `etc/service.conf` and modify to your service config
3. Start a container with `docker-compose up`

## API

### Public Endpoints

1. `GET /api/` - returns the list of loaded holidays (intended for internal use only), i.e.
    ```
    [
     {"sha1":"7ac441071840c1f26d8bff2da1351a078e7d1cca","id":1,"date":"2022-01-17","status":"loaded","desc":"Martin Luther King, Jr. Day"},
     {"sha1":"fcabe6704f7483db0baf369fb7ea9735d470a327","id":2,"date":"2022-02-21","status":"loaded","desc":"Washington's Birthday"},
     {"sha1":"52050b5f4ff3fc5bd995ab5e7b0b70ed557b2db9","id":3,"date":"2022-04-15","status":"loaded","desc":"Good Friday"}
    ]
    ```
2. `GET /api/list_holidays/?holiday_date_start=YYYY-MM-DD&holiday_date_end=YYYY-MM-DD` - returns a list of holidays for the specified date range, i.e.
    ```
    [
    {"date":"2022-01-17","desc":"Martin Luther King, Jr. Day"},
    {"date":"2022-02-21","desc":"Washington's Birthday"},
    {"date":"2022-04-15","desc":"Good Friday"}
    ]
    ```
3. `GET /api/is_holiday/?date_to_check=YYYY-MM-DD` - returns `'Is a holiday.'` if the date is a holiday, or `'Not a holiday.'` if the date is not a holiday.

### Admin Endpoints

1. `POST /api/` - adds a holiday record

   - Request body:
       ```json
       {
        "desc": "Holiday Description", 
        "date": "YYYY-MM-DD"
       }
       ```
   - Example with `curl`:
       ```
       curl -X 'POST' 'http://host/api/' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"desc": "Holiday Description", "date": "YYYY-MM-DD"}' -u 'user:password'
       ```
   - Returns: 
       ```json
       {
        "status":201, 
        "transaction":"Successful"
       }
       ```

2. `POST /api/holidays/` - loads/reloads a list of holidays from https://www.nyse.com/markets/hours-calendars

   - Example with `curl`:
       ```
       curl -X 'POST' 'http://host/api/holidays/' -H 'accept: application/json' -d '' -u 'user:password'
       ```

   - Returns the number of new holidays added, i.e. 
   `{"loaded": #}`


3. `PUT /api/YYYY-MM-DD` - updates an existing holiday record

   - Request body:
       ```json
       {"desc": "New Holiday Description"}
       ```
   - Example with `curl`:
       ```
       curl -X 'PUT' 'http://host/api/YYYY-MM-DD' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"desc": "New Holiday Description"}' -u 'user:password'
       ```
   - Returns: `{"status":200,"transaction":"Successful"}`


4. `DELETE /api/YYYY-MM-DD` - removes a holiday record

   - Returns: `{"status": 200, "transaction": "Successful"}`


5. `DELETE /api/holidays_delete/?holiday_date_start=YYYY-MM-DD&holiday_date_end=YYYY-MM-DD'` - removes holiday records for a specific date range

   - Returns: `{"status": 200, "transaction": "Successful"}`
   
