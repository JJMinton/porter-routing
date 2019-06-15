import numpy as np

from simulator.location import Location
from simulator.porter import Porter
from simulator.sample import Sample


class Hospital:
    def __init__(self, locations, distances):
        """
        Args
        ----
        locations {list}: a list of location names. The first is assumed to be the lab.
        distances {2d array}: an array of times between locations by index
        """
        self.locations = [Location(indx, name) for indx, name in enumerate(locations)]
        self.distances = np.array(distances)
        self.lab_indx = 0
        self.time = 0
        self.porters = []
        self.samples = []

    def add_porter(self, name):
        self.porters.append(Porter(name, self.locations[self.lab_indx]))

    def add_sample(self, name, location, deadline):
        self.samples.append(
            Sample(name, location, deadline, self.locations[self.lab_indx])
        )

    def distances_between(self, from_location, to_location):
        return self.distances[from_location.indx, to_location.indx]

    def increment_time(self, minutes=1):
        self.time += minutes
        for porter in self.porters:
            porter.pass_time(minutes)
        for sample in self.samples:
            sample.pass_time(minutes)

    def locations_by_urgency(self):
        return sorted(self.locations, key=lambda sample: sample.time_to_deadline)

    def __str__(self):
        rtn = f"{self.time} minutes passed\n"

        for porter in self.porters:
            rtn += str(porter) + "\n"
        for sample in self.samples:
            rtn += str(sample) + "\n"
        return rtn
