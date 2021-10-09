import base64
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from typing import NamedTuple

from app.db_connection import redis_con


class Status(Enum):
    PROCESSING = auto()
    PROCESSED = auto()


@dataclass
class Document:
    body: str = ''
    status: Status = Status.PROCESSING.value
    added_time: int = field(default_factory=lambda: datetime.now().timestamp())
    keywords: dict = field(default_factory=dict)
    id: str = None

    def __post_init__(self):
        self.key_prefix = 'DOCUMENT'
        self.status_index = 'status'
        self.keyword_index = 'keyword'

    def get_key(self):
        return f'{self.key_prefix}_{self.id}'

    def get_keyword_index(self, keyword):
        return f'{self.keyword_index}_{keyword}'

    def save(self):
        if self.id is None:
            document_id = redis_con.incr('counter')
            self.id = document_id
        redis_con.set(self.get_key(), json.dumps(asdict(self)))
        redis_con.zadd(self.status_index, {self.id: self.status})

        if self.keywords:
            for kw, rank in self.keywords.items():
                redis_con.zadd(self.get_keyword_index(kw), {self.id: rank})
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

    @staticmethod
    def list():
        prefix = Document().key_prefix
        keys = list(redis_con.scan_iter(f'{prefix}_*'))
        return [int(k.decode().removeprefix(prefix + '_')) for k in keys]

    @staticmethod
    def find_ids_with_status(status: Status):
        res = []
        for doc_id in redis_con.zrangebyscore(
                Document().status_index,
                min=status.value, max=status.value
        ):
            res.append(int(doc_id))
        return res

    @staticmethod
    def documents_with_keyword(keyword):
        res_tuple = NamedTuple("SearchResult", (('doc_id', int), ('score', float)))
        res = []
        for doc_id, score in redis_con.zrevrangebyscore(
                Document().get_keyword_index(keyword),
                min='-inf', max='+inf',
                start=0, num=3,
                withscores=True
        ):
            res.append(res_tuple(int(doc_id), score))
        return res
