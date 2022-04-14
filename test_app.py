from pytest_httpserver import HTTPServer
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from app import app, get_db, get_nyse_url
from requests.auth import HTTPBasicAuth

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def test_create_holiday():
    auth = HTTPBasicAuth(username="admin", password="Lapatusik")
    response = client.post("/",
                           json={"desc": "my first test holiday", "date": "2022-04-14"},
                           auth=auth)
    assert response.status_code == 200, response.text
    response = client.get("/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["desc"] == "my first test holiday"
    assert "id" in data[0]
    assert data[0]["date"] == '2022-04-14'
    response = client.post("/",
                           json={"desc": "my second test holiday", "date": "2022-04-15"},
                           auth=auth)
    assert response.status_code == 200, response.text
    response = client.post("/",
                           json={"desc": "my third test holiday", "date": "2022-04-16"},
                           auth=auth)
    assert response.status_code == 200, response.text


def test_read_all():
    response = client.get("/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["desc"] == "my first test holiday"
    assert "id" in data[0]
    assert data[0]["date"] == '2022-04-14'
    assert len(data) == 3


def test_list_holidays_for_a_date_range():
    response = client.get("/list_holidays/?holiday_date_start=2022-04-14&holiday_date_end=2022-04-15")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["desc"] == "my first test holiday"
    assert data[-1]["desc"] == "my second test holiday"
    response = client.get("/list_holidays/?holiday_date_start=2019-04-14&holiday_date_end=2019-04-15")
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": "No holidays found."}


def test_is_holiday():
    response = client.get("/is_holiday/?date_to_check=2022-04-16")
    assert response.status_code == 200, response.text
    assert response.json() == 'Is a holiday.'
    response = client.get("/is_holiday/?date_to_check=2022-04-18")
    assert response.status_code == 200, response.text
    assert response.json() == 'Not a holiday.'


def test_update_holiday():
    auth = HTTPBasicAuth(username="admin", password="Lapatusik")
    response = client.put("/2022-04-16",
                          json={"desc": "my last test holiday"},
                          auth=auth)
    assert response.status_code == 200, response.text
    response = client.put("/2025-04-16",
                          json={"desc": "my last test holiday"},
                          auth=auth)
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": "No holidays found."}


def test_delete_holiday():
    auth = HTTPBasicAuth(username="admin", password="Lapatusik")
    response = client.delete("/2022-04-16",
                             auth=auth)
    assert response.status_code == 200, response.text
    response = client.delete("/2025-04-16",
                             auth=auth)
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": "No holidays found."}


def test_delete_holidays():
    auth = HTTPBasicAuth(username="admin", password="Lapatusik")
    response = client.delete("holidays_delete/?holiday_date_start=2022-04-14&holiday_date_end=2025-01-31",
                             auth=auth)
    assert response.status_code == 200, response.text
    response = client.delete("holidays_delete/?holiday_date_start=2020-01-01&holiday_date_end=2020-01-31",
                             auth=auth)
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": "No holidays found."}


def test_reload_holidays(httpserver: HTTPServer):
    resp_body = open("testdata/response.html").read()
    httpserver.expect_request("/hours-calendars").respond_with_data(status=200, response_data=resp_body)
    nyse_test_url = httpserver.url_for("/hours-calendars")

    def override_nyse_url():
        return nyse_test_url

    app.dependency_overrides[get_nyse_url] = override_nyse_url

    auth = HTTPBasicAuth(username="admin", password="Lapatusik")
    response = client.post("/holidays/", auth=auth)
    assert response.status_code == 200
    assert response.text == '{"loaded":29}'
