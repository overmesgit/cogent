FROM python:3.9-alpine
WORKDIR /code
ENV FLASK_APP=app/app.py
RUN apk add --no-cache gcc musl-dev libffi-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["pytest", "-s"]
#CMD ["pytest", "-s", "--log-cli-level", "INFO"]