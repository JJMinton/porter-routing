import uuid

class Porter:
    def __init__(self, name, location, id=None):
        self.id = id or uuid.uuid1()
        self.name = name
        self.eta = 0
        self.in_transit = False
        self.location = location
        self.samples = []

    def move_to(self, new_location, hospital):
        assert not self.in_transit
        self.location = new_location
        self.eta = hospital.time + hospital.distance_between(
            self.location, new_location
        )
        self.in_transit = True

    def arrived(self):
        self.in_transit = False
        
    def pick_up_sample(self, sample):
        assert self.location == sample.location and not self.in_transit
        self.samples.append(sample)
        sample.location = self
        self.location.samples.remove(sample)
        
    def pick_up_samples(self):
        if not self.in_transit:
            for sample in self.location.samples:
                if not sample.has_arrived():
                    self.pick_up_sample(sample)
        
    def drop_samples(self):
        if not self.in_transit:
            for sample in self.samples:
                if sample.destination == self.location:
                    sample.location = self.location
                    self.samples.remove(sample)
                    
    @property
    def next_deadline(self):
        return min([sample.deadline for sample in self.samples] + [float('inf')])

    def time_to_destination(self, current_time):
        return max(self.eta - current_time, 0)
        
    def __str__(self):
        if self.in_transit:
            return f"Porter {self.name}, heading to {self.location} with {self.samples} samples with {self.eta} eta."
        return f"Porter {self.name}, at {self.location} with {self.samples} samples."
