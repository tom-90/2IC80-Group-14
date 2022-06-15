from threading import Event
from data.config import Config

class Service:
    config = Config()

    def __init__(self, config):
        self.config = config
        self.stop_signal = Event()

    def start(self):
        pass

    def stop(self):
        self.stop_signal.set()

    def shouldStop(self):
        return self.stop_signal.isSet()