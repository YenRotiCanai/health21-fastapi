import requests
import json
import urllib.request as ur
from urllib.parse import quote
import string

import ortools
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

import pandas as pd

data = {}
data2 = {}
distance_matrix = []
routes = []

def create_data(df):
    """Creates the data."""
    data['API_key'] = 'AIzaSyBR2TL-7XibVRMbpjzkVDyLJzFQ390mAes'  
    data['addresses'] = []

    for i in range(len(df)):
        data['addresses'].append(df['取餐地點'][i])

    return data

def create_distance_matrix(data):
    addresses = data['addresses']
    API_key = data['API_key']
    # print(addresses)
    # print(API_key)

    # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
    max_elements = 100
    num_addresses = len(addresses) # 16 in this example.

    # Maximum number of rows that can be computed per request (6 in this example).
    max_rows = max_elements // num_addresses
    # print("maxrow: "+ str(max_rows))

    # num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
    q, r = divmod(num_addresses, max_rows)
    dest_addresses = addresses
    distance_matrix = []
    
    # Send q requests, returning max_rows rows per request.
    for i in range(q):
        origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)

        # print(origin_addresses)
        # print(response)
        # print(distance_matrix)

    # Get the remaining remaining r rows, if necessary.
    if r > 0:
        origin_addresses = addresses[q * max_rows: q * max_rows + r]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)
    return distance_matrix

def send_request(origin_addresses, dest_addresses, API_key):
    """ Build and send request for the given origin and destination addresses."""
    def build_address_str(addresses):
        # Build a pipe-separated string of addresses
        address_str = ''
        for i in range(len(addresses) - 1):
            address_str += addresses[i] + '|'
        address_str += addresses[-1]
        return address_str

    request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
    origin_address_str = build_address_str(origin_addresses)
    dest_address_str = build_address_str(dest_addresses)

    # print("origin:" + origin_address_str)
    # print("dest:" + dest_address_str)
    # print()

    url = request + '&origins=' + origin_address_str + '&destinations=' + dest_address_str + '&key=' + API_key

    # print(url)
    c = quote(url, safe=string.printable)
    jsonResult = ur.urlopen(c).read()
    response = json.loads(jsonResult)
    return response

def build_distance_matrix(response):
    distance_matrix = []
    for row in response['rows']:
        row_list = [row['elements'][j]['distance']['value'] for j in range(len(row['elements']))]
        distance_matrix.append(row_list)
    return distance_matrix

#----------------#
# Routing #

def create_data_model(distance_matrix, num_vehicles):
    """Stores the data for the problem."""
    # data2 = {}
    data2['distance_matrix'] = distance_matrix
    data2['num_vehicles'] = num_vehicles
    data2['depot'] = 0
    return data2


def print_solution(data2, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    max_route_distance = 0
    for vehicle_id in range(data2['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum of the route distances: {}m'.format(max_route_distance))


def get_routes(solution, routing, manager):
    """Get vehicle routes from a solution and store them in an array."""
    # Get vehicle routes and store them in a two dimensional array whose
    # i,j entry is the jth location visited by vehicle i along its route.
    routes = []
    for route_nbr in range(routing.vehicles()):
        index = routing.Start(route_nbr)
        route = [manager.IndexToNode(index)]
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
        routes.append(route)
    return routes

def main_routing(df, num_vehicles):
    """Entry point of the program"""
    # Create the data.
    data = create_data(df)
    # addresses = data['addresses']
    # API_key = data['API_key']
    distance_matrix = create_distance_matrix(data)
    print("distance matrix:")
    print(distance_matrix)
    print("data:")
    print(data)

    # Instantiate the data problem.
    data2 = create_data_model(distance_matrix, num_vehicles)
    print("data2:")
    print(data2)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data2['distance_matrix']),
                                            data2['num_vehicles'], data2['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data2['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        30000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(50)

    # Setting first solution heuristic.
    # https://developers.google.com/optimization/routing/routing_options
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data2, manager, routing, solution)
    else:
        print('No solution found !')


    routes = get_routes(solution, routing, manager)
    # Display the routes.
    for i, route in enumerate(routes):
        print('Route', i, route)

    return routes

# df = pd.read_csv('SheetDemo3.csv')

# r = main(df, 3)
# print(r)