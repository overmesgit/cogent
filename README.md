## About

Best keyword match finding service.

Supports:
* add document
* list documents
* find document

## Usage

`docker-compose up`

Add document

`curl`

Find document

`curl`

List documents

`curl`

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