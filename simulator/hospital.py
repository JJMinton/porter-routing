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
        if isinstance(locations[0], Location):
            self.locations = locations
        else:
            self.locations = [Location(name) for name in locations]
        self.distances = np.array(distances)
        self.lab = self.locations[0]
        self.time = 0
        self.porters = []
        self.samples = []

    def add_porter(self, name, id, current_location):
        self.porters.append(Porter(name, self.get_location(current_location), id=id))

    def add_sample(self, name, id, location, deadline):
        self.samples.append(
            Sample(name, self.get_location(location), deadline, self.lab)
        )

    def get_location(self, location):
        if isinstance(location, Location):
            return location
        if isinstance(current_location, str):
            return [loc for loc in self.locations if loc.id==current_location][0]

    def list_locations_without_samples(self):
        return [
            loc for loc in self.locations
            if not loc.samples and not loc == self.lab
        ]

    def drop_locations_without_samples(self):
        while self.list_locations_without_samples():
            self.remove_location_and_samples(self.list_locations_without_samples()[0])

    def remove_porter_and_samples(self, porter):
        self.samples = [
            sample for sample in self.samples if sample.location != porter
        ]
        self.porters.remove(porter)

    def remove_location_and_samples(self, location):
        self.samples = [
            sample for sample in self.samples if sample.location != location
        ]
        if location != self.lab:
            location_indx = self.locations.index(location)
            self.distances = np.delete(self.distances, location_indx, axis=0)
            self.distances = np.delete(self.distances, location_indx, axis=1)
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
        rtn = Hospital(copy(self.locations), copy(self.distances))
        rtn.lab = self.lab
        rtn.time = self.time
        rtn.porters = copy(self.porters)
        rtn.samples = copy(self.samples)
        return rtn
