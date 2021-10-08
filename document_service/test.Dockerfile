FROM python:3.7-alpine
WORKDIR /code
ENV FLASK_APP=app.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["pytest"]