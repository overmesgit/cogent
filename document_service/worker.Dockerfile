FROM python:3.9-alpine
WORKDIR /code
RUN apk add --no-cache gcc
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["rq", "worker", "-u", "redis://redis"]