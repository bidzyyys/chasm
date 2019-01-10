from abc import ABC


class Service(ABC):

    def __start__(self, stop_condition):
        raise NotImplementedError

    def __stop__(self):
        raise NotImplementedError


class ServicesManager:
    def __init__(self, services_to_run: [Service], logger):
        self._should_close = False
        self.services = services_to_run
        self._logger = logger

    def __enter__(self):
        self._logger.info("Starting managed services")

        for service in self.services:
            service.__start__(self.should_close)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._should_close = True
        self._logger.info("Shutting down.")

        for service in self.services.reverse():
            service.__stop__()

    def should_close(self):
        return self._should_close
