import io
import re
from typing import TYPE_CHECKING

from pdfminer.high_level import extract_text

if TYPE_CHECKING:
    from app import Document


def process_document(document: 'Document') -> None:
    text = extract_text(io.BytesIO(document.decode_body()))
    print(text)
    resp = re.findall(r'\b\w{3,}\b', text)
    print(resp)
