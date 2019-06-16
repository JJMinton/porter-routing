from datetime import datetime
import uuid

class Location:
    def __init__(self, name, id=None):
        self.id = uuid.uuid1() if id is None else id
        self.name = name
        self.samples = []

    def add_sample(self, sample):
        self.samples.append(sample)

    @property
    def next_deadline(self):
        return min([sample.deadline for sample in self.samples] + [datetime.max])

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.id}({self.name})"
