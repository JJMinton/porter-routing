import uuid

class Location:
    def __init__(self, name, id=None):
        self.id = id or uuid.uuid1()
        self.name = name
        self.samples = []
    
    def add_sample(self, sample):
        self.samples.append(sample)
        
    @property
    def next_deadline(self):
        return min([sample.deadline for sample in self.samples] + [float('inf')])
    
    def __str__(self):
        return self.name
