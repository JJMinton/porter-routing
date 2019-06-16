from copy import copy

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
        self.locations = [Location(name) for name in locations]
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

    def remove_porter_and_samples(self, porter):
        self.samples = [
            sample for sample in self.samples if sample.location != porter
        ]
        self.porters.remove(porter)

    def remove_location_and_samples(self, location):
        self.samples = [
            sample for sample in self.samples if sample.location != location
        ]
        self.locations.remove(location)

    def distances_between(self, from_location, to_location):
        return self.distances[from_location.indx, to_location.indx]

    def increment_time(self, minutes=1):
        self.time += minutes
        for porter in self.porters:
            porter.pass_time(minutes)
        for sample in self.samples:
            sample.pass_time(minutes)

    def locations_by_urgency(self):
        return sorted(self.locations, key=lambda location: location.time_to_next_deadline(0))

    def __str__(self):
        rtn = f"{self.time} minutes passed\n"

        for porter in self.porters:
            rtn += str(porter) + "\n"
        for sample in self.samples:
            rtn += str(sample) + "\n"
        return rtn

    def __copy__(self):
        rtn = Hospital([loc.name for loc in self.locations], copy(self.distances))
        rtn.lab_indx = self.lab_indx
        rtn.time = self.time
        rtn.porters = copy(self.porters)
        rtn.samples = copy(self.samples)
        return rtn
