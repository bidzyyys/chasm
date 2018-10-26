from abc import abstractmethod, ABC


class Serializer(ABC):
    @staticmethod
    @abstractmethod
    def to_bytes(obj: object): bytes

    @staticmethod
    @abstractmethod
    def from_bytes(b: bytes): object

