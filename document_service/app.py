import base64
import io
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum, auto

from flask import Flask, request
from redis import Redis
from rq import Queue

from task import process_document

redis_con = Redis(host='redis')
q = Queue(connection=redis_con)

app = Flask(__name__)


class Statuses(Enum):
    PROCESSING = auto()


@dataclass
class Document:
    body: str = ''
    status: Statuses = Statuses.PROCESSING.value
    added_time: int = field(default_factory=lambda: datetime.now().timestamp())
    keywords: dict = field(default_factory=dict)
    id: str = None

    def __post_init__(self):
        self.key_prefix = 'DOCUMENT'

    def get_key(self):
        return f'{self.key_prefix}_{self.id}'

    def save(self):
        document_id = redis_con.incr('counter')
        self.id = document_id
        redis_con.set(self.get_key(), json.dumps(asdict(self)))
        redis_con.zadd('status', {self.status: document_id})
        return self

    def decode_body(self):
        return base64.b64decode(self.body)

    @staticmethod
    def get_encoded_body(data):
        return base64.b64encode(data).decode()

    @staticmethod
    def get_document(document_id):
        document = Document(id=document_id)
        resp = redis_con.get(document.get_key())
        if resp:
            return Document(**json.loads(resp))
        else:
            return None


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
    return {'document_id': document.id, 'status': Statuses(document.status).name}


@app.route('/document/')
def document_list():
    documents = redis_con.keys('DOCUMENT_*')
    return 'Hello World!' + documents


@app.route('/document/find')
def document_find():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
