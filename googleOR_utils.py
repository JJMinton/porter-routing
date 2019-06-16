from datetime import timedelta


def print_solution(data, manager, routing, assignment):
    """Prints assignment on console."""
    total_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        total_distance += route_distance
    print('Total Distance of all routes: {}m'.format(total_distance))


def solution_to_dict(manager, routing, assignment, hospital):
    rtn = {}
    for porter_indx, porter in enumerate(hospital.porters):
        rtn[porter.id] = [(porter.location, porter.eta), ]
        index = routing.Start(porter_indx)

        while not routing.IsEnd(index):
            previous_index = index
            index = assignment.Value(routing.NextVar(index))

            location_indx = manager.IndexToNode(index)
            location_indx = 0 if location_indx == len(hospital.locations) else location_indx
            location = hospital.locations[location_indx]
            eta = rtn[porter.id][-1][1] + timedelta(
                minutes=routing.GetArcCostForVehicle(previous_index, index, porter_indx)
            )

            rtn[porter.id].append((location, eta))

        # add time to deliver to lab
        rtn[porter.id] = [(x[0], x[1], eta) for x in rtn[porter.id]]

    return rtn

