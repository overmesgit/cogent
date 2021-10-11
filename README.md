## About

Service that finds the best keyword match in documents database.

Supports:
* add document
* list documents
* find document

## Install
```bash
git clone https://github.com/overmesgit/cogent && cd cogent
```

## Run tests
```bash
docker-compose -f docker-compose-test.yml up --exit-code-from test -t 1 --build
```

## Usage
Run services:

```bash
docker-compose up  --build -t 1
```

Add document:

```bash
curl -F "file=@document_service/app/test/simple3.pdf" http://localhost:5000/document/add
```

Find document:

```bash
curl http://localhost:5000/document/find?keyword=Text1
```

List documents:

```bash
curl http://localhost:5000/document/
```

## Services
Service consists from 2 main programs:

1. Frontend Service

* Download document to db
* Schedule document for processing
* Find document with keyword
* Show document list

2. Worker Service

* Take task from queue
* Process document and get keywords
* Update document

They communicate between them through Redis database with rq library.
Frontend service receive document from user, load it in database and start 
worker job. Worker process documents and update it in db.
There can be multiple fronted and worker services.

### Supported formats

* pdf
* txt

### Additional notice

If scalability in high priority I would also consider to use AWS Lambda functions,
because with simple architecture very high scalability can be reached.

With current structure services can be deployed to AWS ECS service. Auto-scaling also can be
configured.

In production documents should be downloaded to S3.

Redis isn't reliable persistence storage, for real application I would prefer some SQL database.
I have used Redis because I already have it for workers queue.

It was interesting assigment. I didn't work with docker-compose and redis before, so it took
some time to set it up.