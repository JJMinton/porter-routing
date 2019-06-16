from copy import copy
from datetime import datetime

from simulator.porter import Porter
from solver_googleOR import solver as solver_without_urgency


def solver(hospital, current_time):

    tmp_hospital = copy(hospital)
    final_route = {}
    tmp_hospital.drop_locations_without_samples()
    
    while True:
        if not tmp_hospital.samples:
            print("success")
            break

        if not tmp_hospital.porters:
            raise NotImplementedError(
                "Every porter has a current task but all the samples haven't been"
                " accounted for. This situation hasn't been solved for yet."
            )
            #TODO: handle porters subsequent jobs
            break

        urgency = sorted(
            tmp_hospital.locations + tmp_hospital.porters,
            key=lambda x: x.next_deadline
        )[0]

        time_to_next_urgency = (urgency.next_deadline - current_time).total_seconds()/60

        # Solve for most urgent to get back
        route = solver_without_urgency(tmp_hospital, max_time=time_to_next_urgency)
        if not route:
            raise NotImplementedError(
                "We failed to deliver a sample in time and this situation hasn't been"
                " solved for yet."
            )
            # TODO: handle failed solve here

        # Find porter and route containing most urgent sample
        if isinstance(urgency, Porter):
            porter = urgency
            porter_indx = tmp_hospital.index(porter)

        else:
            for porter_indx, porter in enumerate(tmp_hospital.porters):
                if urgency in [stop[0] for stop in route[porter.id]]:
                    break
        # Add that porters tasking to final routing
        final_route[porter.id] = route[porter.id] 

        #Remove that porters tasking from next iteration
        tmp_hospital.remove_porter_and_samples(porter)
        for stop in route[porter.id]:
            tmp_hospital.remove_location_and_samples(stop[0])

    return final_route


