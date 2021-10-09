## About

Service that finds the best keyword match in documents database.

Supports:
* add document
* list documents
* find document

## Usage

Run services:

```bash
docker-compose up
```

Add document

```bash
curl
```

Find document

`curl`

List documents

`curl`

## Run tests
docker-compose -f docker-compose-test.yml up --exit-code-from test -t 1 --build

## Services

1. Frontend Service

* Download document to db
* Create task
* Find doc
* Document list

2. Worker Service

* Take task from queue
* Process document
* Save to db

### TODO

Lambda architecture
Documents should be downloaded to S3