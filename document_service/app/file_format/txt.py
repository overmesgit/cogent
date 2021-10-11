import logging
import re

from app.file_format.base import BaseFileProcessor

logger = logging.getLogger(__name__)


class TXTProcessor(BaseFileProcessor):
    file_format = 'txt'

    def get_file_text(self, file_data):
        return re.findall(r'\b\w{3,}\b', file_data.decode('utf-8'))

    def is_valid_file(self, file_data):
        try:
            return bool(file_data.decode('utf-8'))
        except Exception as ex:
            logger.error('ProcessDocumentError %s', ex)
            return False
