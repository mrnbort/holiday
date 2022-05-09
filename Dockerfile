FROM python:3.8

WORKDIR /code

RUN python -m pip install --upgrade pip
RUN pip install -U setuptools

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY *.py /code/
COPY testdata /code/testdata

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
