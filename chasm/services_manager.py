import concurrent
import time
from abc import ABC
from concurrent.futures.thread import ThreadPoolExecutor

from termcolor import colored

from chasm.maintenance.logger import Logger


class Service(ABC):

    def start(self, stop_condition):
        raise NotImplementedError

    def is_running(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class LazyService:
    def __init__(self, name, klass, required_services=None, *args, **kwargs):
        self.klass = klass
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.required = required_services or []

    def build(self, services):
        required = {name: service for name, service in zip(self.required, services)}
        return self.name, self.klass(*self.args, **{**self.kwargs, **required})


class ServicesManager:
    def __init__(self, services_to_run: [LazyService]):
        self._running_services: {str: Service} = {}
        self._services_to_run: [LazyService] = services_to_run
        self._logger = Logger('chasm.manager')
        self._should_close = True

    def __enter__(self):
        self._should_close = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == KeyboardInterrupt:
            self._logger.info("Caught ctrl-c event. Closing.")

        self._should_close = True

        self._logger.info('Stopping services.')
        for name, service in self._running_services.items():
            self._logger.info(f'Stopping service: {name}')
            service.stop()
            self._logger.info(f'Stopped service: {name}')

        return exc_type == KeyboardInterrupt

    def run(self):

        self.start_services()
        self.watch()

    def start_services(self):
        self._logger.info('Starting services.')
        for lazy in self._services_to_run:

            required = []
            for requirement in lazy.required:
                required.append(self._running_services[requirement])

            name, service = lazy.build(required)
            self._start_service(name, service)
            self._running_services[name] = service

    def watch(self):
        should_finish = False
        while not should_finish:
            time.sleep(10)
            for name, service in self._running_services.items():
                if not service.is_running():
                    self._logger.error(colored(f'Service {name} not running - closing application.', 'red'))
                    should_finish = True

    def _start_service(self, name, service):

        with ThreadPoolExecutor(max_workers=1) as executor:
            task = executor.submit(service.start, self.should_close)
            self._logger.info(f'Starting service: {name}')
            try:
                if task.result(1):
                    self._logger.info(f'Started service: {name}')
                else:
                    self._logger.error(colored(f'Failed to start a service: {name}', 'red'))
                    raise RuntimeError
            except concurrent.futures.TimeoutError:
                self._logger.error(colored(f'Failed to start a service due to a timeout: {name}'), 'red')
                raise

    def should_close(self):
        return self._should_close
