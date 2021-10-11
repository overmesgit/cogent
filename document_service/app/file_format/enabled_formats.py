from typing import Type

from app.file_format.base import BaseFileProcessor
from app.file_format.pdf import PdfProcessor
from app.file_format.txt import TXTProcessor

ENABLED_FORMATS = [
    PdfProcessor,
    TXTProcessor
]

FORMAT_TO_PARSER: dict[str, Type[BaseFileProcessor]] = {p.file_format: p for p in ENABLED_FORMATS}
