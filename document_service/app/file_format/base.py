from abc import ABC, abstractmethod


class BaseFileProcessor(ABC):

    @abstractmethod
    def is_valid_file(self, file_data) -> bool:
        pass

    @abstractmethod
    def get_file_text(self, file_data) -> list[str]:
        pass
