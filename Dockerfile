FROM python:3.8

WORKDIR /home/tides

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0","--port=80"]

