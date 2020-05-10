import inspect

from systems.serialization import JSONEncoder

class BlobLogger():
    _instance = None

    @staticmethod
    def setup():
        assert not BlobLogger._instance
        BlobLogger._instance = BlobLogger()
        return BlobLogger._instance

    @staticmethod
    def get():
        assert BlobLogger._instance
        return BlobLogger._instance

    def __init__(self):
        assert not BlobLogger._instance
        BlobLogger._instance = self
        self.items = []
        self.last_allocated_id = 0
        self.current_id = None

    def allocate_id(self):
        self.last_allocated_id += 1
        return self.last_allocated_id

    def set_active_event(self, event_id):
        self.current_id = event_id
        return self

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.current_id = None

    def log(self, data, attach_id=True, event_id=None):
        if event_id:
            data["event_id"] = event_id
        elif attach_id:
            assert self.current_id
            data["event_id"] = self.current_id

        frame = inspect.stack()[1]
        data["where"] = { "file" : frame.filename,
                          "lineno" : frame.lineno }

        self.items.append(data)

    def serialize(self):
        return {
            "items" : self.items,
            "last_allocated_id" : self.last_allocated_id,
            "current_id" : self.current_id
        }
