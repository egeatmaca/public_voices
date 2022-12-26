FROM apache/spark:latest

USER root

RUN apt-get update && \
    apt-get install -y python3 python3-pip

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN python3 manage.py makemigrations

RUN python3 manage.py migrate

ENTRYPOINT [ "python3" ]

CMD [ "manage.py", "runserver", "0.0.0.0:8000" ]