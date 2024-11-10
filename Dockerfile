# TODO Proper volume support for ./static/img/monitor/ data

FROM debian
WORKDIR /usr/local/src

RUN apt-get update

# Dependency of pydantic-core
RUN apt-get install -y cargo

RUN apt-get install -y python3
RUN apt-get install -y python3-pip

# We don't care about other system usage because this is isolated
COPY requirements.txt ./
RUN pip install --break-system-packages -r ./requirements.txt

RUN useradd app
USER app

COPY . .

EXPOSE 8080

CMD ["uvicorn", "monitor:app", "--host", "0.0.0.0", "--port", "8080"]
