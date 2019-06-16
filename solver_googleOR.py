"""Simple Pickup Delivery Problem (PDP)."""
from __future__ import print_function
from pprint import pprint

import numpy as np

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from googleOR_utils import print_solution


def create_data_model(hospital):
    """Stores the data for the problem."""
    data = {}

    # Add shadow node for lab because start/end can't be current delivery location
    dummy_lab_indx = len(hospital.locations)
    distances = np.zeros(tuple(idx+1 for idx in hospital.distances.shape))
    distances[:dummy_lab_indx,:dummy_lab_indx] = hospital.distances 
    distances[dummy_lab_indx, 1:] = hospital.distances[0,:]
    distances[1:, dummy_lab_indx] = hospital.distances[:,0]

    data['distance_matrix'] = distances
    data['pickups_deliveries'] = [
        (
            hospital.locations.index(sample.location),
            hospital.locations.index(sample.destination)
        )
        for sample in hospital.samples if not sample.has_arrived()
    ]
    data['num_vehicles'] = len(hospital.porters)
    data['end_locations'] = [dummy_lab_indx]*data['num_vehicles']
    data['start_locations'] = [
        hospital.locations.index(porter.location) or dummy_lab_indx
        for porter in hospital.porters
    ]

    return data

def solver(hospital, max_time=480):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(hospital)
    pprint(data)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['start_locations'], data['end_locations'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Define cost of each arc.
    def distance_callback(from_index, to_index):
        """Returns the manhattan distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Define Transportation Requests.
    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(
                delivery_index))
        routing.solver().Add(
            distance_dimension.CumulVar(pickup_index) <=
            distance_dimension.CumulVar(delivery_index))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if assignment:
        print_solution(data, manager, routing, assignment)
    else:
        print("Failed")


if __name__ == "__main__":
    main()
