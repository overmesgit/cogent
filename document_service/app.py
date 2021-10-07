from flask import Flask
from redis import Redis
from rq import Queue

from task import process_document

q = Queue(connection=Redis(host='redis'))

app = Flask(__name__)


@app.route('/document/add')
def document_add():
    q.enqueue(process_document)
    return 'Hello World!'


@app.route('/document/')
def document_list():
    return 'Hello World!'


@app.route('/document/find')
def document_list():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
