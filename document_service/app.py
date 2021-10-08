from flask import Flask
from redis import Redis
from rq import Queue

from task import process_document

redis_con = Redis(host='redis')
q = Queue(connection=redis_con)

app = Flask(__name__)


@app.route('/document/add')
def document_add():
    q.enqueue(process_document)
    res = redis_con.get('counter')
    if not res:
        res = 1
    else:
        res = 1 + int(res)
    redis_con.set('counter', res)
    return f'Hello World! {res}'


@app.route('/document/')
def document_list():
    return 'Hello World!'


@app.route('/document/find')
def document_find():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
