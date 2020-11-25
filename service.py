from datetime import datetime

class ServiceState():

    def __init__(self, status: str, last_changed_time: datetime):
        self.status = status
        self.last_changed_time = last_changed_time

    def get_elapsed_time(self):
        return datetime.utcnow() - self.last_changed_time