import inspect
from abc import ABC


class Validator(ABC):

    def prepare(self, obj):
        raise NotImplementedError

    def validate(self, obj):
        prepared_parameters = self.prepare(obj)
        methods = [getattr(self, method) for method in dir(self) if method.startswith('check_')]

        for method in methods:
            parameters = {k: prepared_parameters[k] for k in inspect.getfullargspec(method).args if not k == 'self'}
            method(**parameters)
