import openrouteservice
import folium
import json
import os.path

from shapely import wkt, geometry
from pprint import pprint
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from openrouteservice import directions

# The purpose of this file is to generate a route for three different groups
# Using openrouteservice API and ortools, get the best route to visit
# each parking location in every group, and plot onto a map

# OUTPUT: three_route_enforcement.html = the visualization for an optimal route each group could take
#         CondensedRoutes = a collection of .json files that represent the optimal route by parking name and duration
#         FullRoutes = full route info with directions returned by the openrouteservice API

# read in all parking coordinates, seperated py group

garage_matrix_g1 = None
garage_matrix_g2 = None
garage_matrix_g3 = None

def read_coords_from_3_group_json():
    coords = []
    group1 = ()
    group2 = ()
    group3 = ()

    with open('route_visualization/garage_coordinates_3_groups.json') as json_file:
        data = json.load(json_file)
        for garage in data:
            nextGarage = (garage['longitude'], garage['latitude'], )

            # seperate each parking location by group
            if(garage['group'] == 1):
                group1 = (nextGarage,) + group1
            elif(garage['group'] == 2):
                group2 = (nextGarage,) + group2
            elif(garage['group'] == 3):
                group3 = (nextGarage,) + group3

    # add each group to overall coords object
    coords.append(group1)
    coords.append(group2)
    coords.append(group3)

    return coords

# Put parking location markers onto the map
def load_markers(m):
    with open('route_visualization/garage_coordinates_3_groups.json') as json_file:
        data = json.load(json_file)
        for garage in data:
            folium.Marker(
                location=[garage['latitude'], garage['longitude']],
                popup= garage['name'],
                icon=folium.Icon(icon='car', prefix='fa')
            ).add_to(m)
    return m

# Get the matrices for each group's route
def get_matrices(groupNum, clnt, coords):
    request = {'locations': coords[groupNum],
           'profile': 'driving-car',
           'metrics': ['duration']}
    
    return clnt.distance_matrix(**request)

# cost function to compare distances for optimal routes
def get_distance_g1(from_id, to_id):
    from_id = from_id -1
    to_id = to_id -1
    return int(garage_matrix_g1['durations'][from_id][to_id])

def get_distance_g2(from_id, to_id):
    from_id = from_id -1
    to_id = to_id -1
    return int(garage_matrix_g2['durations'][from_id][to_id])

def get_distance_g3(from_id, to_id):
    from_id = from_id -1
    to_id = to_id -1
    return int(garage_matrix_g3['durations'][from_id][to_id])

# using ortools, determine the cost and find the optimal coordinate (parking loccation) order for a route
def get_path(garage_matrix, coords, matrixNum):
    tsp_size = len(coords)
    num_routes = 1
    start = 0

    optimal_coords = []


    if tsp_size > 0:
        manager = pywrapcp.RoutingIndexManager(tsp_size, num_routes, start)
        routing = pywrapcp.RoutingModel(manager)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()

        # Create the distance callback, which takes two arguments (the from and to node indices)
        # returns the distance between these nodes.
        dist_callback = None
        if(matrixNum == 1):
            dist_callback = routing.RegisterTransitCallback(get_distance_g1)
        if(matrixNum == 2):
            dist_callback = routing.RegisterTransitCallback(get_distance_g2)
        elif(matrixNum == 3):
            dist_callback = routing.RegisterTransitCallback(get_distance_g3)

        routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)
        assignment = routing.SolveWithParameters(search_parameters)
        if assignment:
            index = routing.Start(start)
            for node in range(routing.nodes()):
                optimal_coords.append(coords[manager.IndexToNode(index)-1])
                index = assignment.Value(routing.NextVar(index))

    return optimal_coords

# get the color properties for each route trace
def style_function(color):
    return lambda feature: dict(color=color,
                              weight=3,
                              opacity=1)

# Apply the optimal path trace for each group on the map
def get_path_mapped(optimal_coords, m, clnt, groupNum):
    request = {'coordinates': optimal_coords,
           'profile': 'driving-car',
           'geometry': 'true',
           'format_out': 'geojson',
          }

    optimal_route = clnt.directions(**request)

    # dump full optimal route result from the api into json
    with open('route_visualization/FullRoutes/full_route_g' + str(groupNum) + '.json', 'w') as outfile:
        json.dump(optimal_route, outfile)

    color = ''

    if(groupNum == 1):
        color = '#6666ff'
    elif(groupNum == 2):
        color = '#6ffff6'
    elif(groupNum == 3):
        color = '#ff6666'

    folium.features.GeoJson(data=optimal_route,
                            name='Optimal Parking Patrol',
                            style_function=style_function(color),
                        overlay=True).add_to(m)

# save the route and duration between each step to a json file for data generation later
def save_routes(groupNum, optimal_coords):

    with open('route_visualization/garage_coordinates_3_groups.json') as all_coords:
        with open('route_visualization/FullRoutes/full_route_g'+str(groupNum)+'.json') as full_route:
            garages = json.load(all_coords)
            full_enforce_route = json.load(full_route)
            time = 0
            garageTimePair = ()
            route = []
            inx = -1

            for coordPair in optimal_coords:
                for garage in garages:
                    
                    if(inx != -1):
                        segment = full_enforce_route['features'][0]['properties']['segments'][inx]
                    if(garage['latitude'] == coordPair[1] and garage['longitude'] == coordPair[0]):
                        if(inx == -1):
                            garageTimePair = (garage['name'], 0)
                        else:
                            garageTimePair = (garage['name'], segment['duration'])
                        route.append(garageTimePair)
                inx = inx + 1
                
    with open('route_visualization/CondensedRoutes/condensed_route_g'+str(groupNum)+'.json', "w") as outfile:
        json.dump(route, outfile)

def start():
    api_key = ''
    with open('route_visualization/api_key.txt', "r") as api_key_file:
        api_key = api_key_file.read()
        
    clnt = openrouteservice.Client(key=api_key)

    coords = read_coords_from_3_group_json()

    mapCenter = (38.945830, -92.328912)

    m = folium.Map(location=(mapCenter[0], mapCenter[1]), zoom_start=14)
    m = load_markers(m)

    global garage_matrix_g1
    garage_matrix_g1 = get_matrices(0, clnt, coords)
    global garage_matrix_g2
    garage_matrix_g2 = get_matrices(1, clnt, coords)
    global garage_matrix_g3
    garage_matrix_g3 = get_matrices(2, clnt, coords)

    optCoordsG1 = get_path(garage_matrix_g1, coords[0], 1)
    optCoordsG2 = get_path(garage_matrix_g2, coords[1], 2)
    optCoordsG3 = get_path(garage_matrix_g3, coords[2], 3)

    get_path_mapped(optCoordsG1, m, clnt, 1)
    get_path_mapped(optCoordsG2, m, clnt, 2)
    get_path_mapped(optCoordsG3, m, clnt, 3)

    save_routes(1, optCoordsG1)
    save_routes(2, optCoordsG2)
    save_routes(3, optCoordsG3)

    m.save('route_visualization/three_route_enforcement.html')
