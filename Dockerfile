FROM python:3.7-slim

WORKDIR /src
EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "--timeout=30", "--workers=2", "app.api:app"]

RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /src/
RUN pip3 install -r requirements.txt

ENV PYTEST_ADDOPTS "-x"

COPY . /src
RUN cd /src && python3 setup.py develop
