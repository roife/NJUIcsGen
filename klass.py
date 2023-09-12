from datetime import datetime

class Klass:
    def __init__(self, name: str, teacher: str, loc: str, time_range: str, code: str, start_time: datetime, end_time: datetime):
        self.name = name
        self.teacher = teacher
        self.loc = loc
        self.time_range = time_range
        self.code = code
        self.start_time = start_time
        self.end_time = end_time