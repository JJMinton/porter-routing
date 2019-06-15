class Location:
    def __init__(self, indx, name):
        self.indx = indx
        self.name = name
        self.samples = []
    
    def add_sample(self, sample):
        self.samples.append(sample)
        
    def time_to_next_deadline(self, current_time):
        return min([sample.time_to_deadline(current_time) for sample in self.samples] + [float('inf')])
    
    def __str__(self):
        return self.name
