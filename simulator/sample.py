from simulator.location import Location

class Sample:
    def __init__(self, name, location, deadline, destination):
        self.name = name
        self.location = location
        self.deadline = deadline
        self.destination = destination
        self.location.add_sample(self)

    def time_to_deadline(self, current_time):
        return self.deadline - current_time

    def is_late(self, current_time):
        return self.time_to_deadline(current_time) < 0
    
    def has_arrived(self):
        return self.location == self.destination
    
    def in_transit(self):
        return not isinstance(self.location, Location)
    
    def __str__(self):
        if self.has_arrived():
            return f"Sample {self.name} arrived."
        if self.in_transit():
            return f"Sample {self.name} on the way to {self.location.location} with self.location"
        return f"Sample {self.name} at {self.location.name} with a deadline of {self.deadline}"
