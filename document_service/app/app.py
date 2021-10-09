import io

from flask import Flask, request
from rq import Queue

from app.db_connection import redis_con
from app.document import Document, Status
from app.task import process_document

q = Queue(connection=redis_con)

app = Flask(__name__)


@app.route('/document/add', methods=['POST'])
def document_add():
    if 'file' not in request.files or request.files['file'].filename == '':
        return {'error': 'no file'}
    file = request.files['file']

    file_base64 = ''
    if file and file.filename.endswith('.pdf'):
        buffer = io.BytesIO()
        file.save(buffer)
        file_base64 = Document.get_encoded_body(buffer.getvalue())

    document = Document(body=file_base64)
    document.save()
    q.enqueue(process_document, document)
    return {'document_id': document.id, 'status': Status(document.status).name}


@app.route('/document/')
def document_list():
    documents = redis_con.keys('DOCUMENT_*')
    return 'Hello World!' + documents


@app.route('/document/find')
def document_find():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
