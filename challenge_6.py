import csv
import heapq

#Function: Load a CSV

def load_csv(filename):
    data = []

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

# Load the CSVs
trains = load_csv("train.csv")
shipment_priorities = load_csv("shipment_priority.csv")
rail_connections = load_csv("rail_network_map.csv")
shipments = load_csv("shipments.csv")

# Display File-Loading Summary
print("Python Rail System")
print("=" * 40)
print(f"Trains loaded: {len(trains)}")
print(f"Shipment priorities loaded: {len(shipment_priorities)}")
print(f"Rail connections loaded: {len(rail_connections)}")
print(f"Shipments loaded: {len(shipments)}")
print()
print("Ready for route planning")

# Create the priority lookup dictionary
#Priority Lookup
priority_lookup = {}
for priority_row in shipment_priorities:
    shipment_type = priority_row["shipment_type"]
    priority_number = int(priority_row["priority"])

    priority_lookup[shipment_type] = priority_number

#Add Priority to each shipment using lookup
for shipment in shipments:
    shipment_type = shipment["shipment_type"]
    shipment["priority"] = priority_lookup[shipment_type]

#Sorting shipments by priority
shipments.sort(key=lambda shipment: shipment["priority"])

for shipment in shipments:
    print(shipment)


# Display Shipments after sorting
print("\nShipments sorted by priority")
print("=" * 40)
for shipment in shipments:
    print(
        f"Priority: {shipment['priority']} | "
        f"{shipment['shipment_id']} | "
        f"{shipment['shipment_type']} | "
        f"{shipment['origin_station']} | -> "
        f"{shipment['destination_station']} | "
    )
#Build the graph
rail_graph = {}

for connection in rail_connections:
    origin = connection["start_station"]
    destination = connection["end_station"]

    #Read the track time and delay from csv
    track_time = int(connection["travel_time_minutes"])
    delay = int(connection["delay_minutes"])

    # Calculate the total time for this railroad connection
    total_travel_time = track_time + delay

    #Add the stations if they are not already in the graph
    if origin not in rail_graph:
        rail_graph[origin] = {}

    if destination not in rail_graph:
        rail_graph[destination] = {}
    # Add the connection in both direction
    rail_graph[origin][destination] = total_travel_time
    rail_graph[destination][origin] = total_travel_time

#Display the railroad graph
print("\nRailraod Network")
print("=" * 40)

for station, connections in rail_graph.items():
    print(f"\nStation: {station}")

    for neighbor, travel_time in connections.items():
        print(f" -> {neighbor} -> {travel_time} total minutes")


#Select the Next Shipment for Route Planning
#Beachse the hsipment list is sorted, index 0 contains
# the hsipment with teheihghest priority

if shipments:
    current_shipment = shipments[0]

    start_station = shipments[0]["origin_station"]
    destination_station = current_shipment["destination_station"]

    print("\nNEXT SHIPMENT TO ROUTE")
    print("=" * 40)
    print(f"Shipment ID: {current_shipment['shipment_id']}")
    print(f"Shipment Type: {current_shipment['shipment_type']}")
    print(f"Shipment Priority: {current_shipment['priority']}")
    print(f"Route: {start_station} -> {destination_station}")
else:
    print("\nNo shipmnents are available for route planning")

## Begin Dijkstra Algorithm
print("\n Starting Dijkstra's Algorithm...")
print(f"Finding the fastest route from {start_station} to {destination_station}")

#Initialize the distance table
#Create an empty dictionary to stare the shortest known
#travel time from the starting station to every station
distances = {}

#set every station's distance to infinity.
#This means no route has been discovered yet
for station in rail_graph:
    distances[station] = float("inf")

#The starting station is always zero minutes away
#because the huorney beings there
distances[start_station] = 0

#display the initial distance tables
print("\n INITIAL DISTAANCE TABLE")
print("=" * 40)

for station, distance in distances.items():
    if distance == float("inf"):
        print(f"{station}: infinity")
    else:
        print(f"{station}: {distance}")

# Initialize previous table to store breadcrumbs
previous = {}

#At the start of the algorithm, no station has a predecessor.
for station in rail_graph:
    previous[station] = None

#Display the initial previous-station table
print("\n INITIAL PREVIOUS-STATION TABLE")
print("=" * 40)

for station, previous_station in previous.items():
    print(f"{station} -> {previous_station}")

#Initialize Visited Set
#Create an empty set to store station that have been
# completely processed

visited = set()

#Display the initial visited set
print("\n INITIAL VISITED SET")
print("+" * 40)
print(visited)

# Initialize the priority Queue
#Create an empty priority queue
#This queue will store stations waiting to be explored
priority_queue = []

#Add the sarting station to the priority queue
#The tuple contains
# (Current shortest travel time, station name)
# The starting station always begins with a travel time of 0

heapq.heappush(priority_queue, (0, start_station))

#Display the initial priorrity queue
print("\nInitial Priority Queue")
print("=" * 40)
print(priority_queue)

#Begin Dijkstra's Search

while priority_queue:
    current_distance, current_station = heapq.heappop(priority_queue) #heeppop() removes the smmlest item
    if current_station in visited:
        continue
    #Mark this station as complete
    visited.add(current_station)

    print()
    print(f"Now exploring: {current_station}")
    print(f"Current travel time: {current_distance} minutes")

#Now that we've arrived at a station...time to explore neighboring stations
#This loop asks the question, from the station I am currently at, where can I go next and how long will it take to get there
for neighbor, travel_time in rail_graph[current_station].items():
    print(f"Neighbor: {neighbor}")
    print(f"Travel Time: {travel_time} minutes")

    #Calculate the new travel time for e3ach neighboring station, Dijkstra calculates how long it would take to reach that station
    #new calculated travel time is compared to the current best travel travel_time#
    #Calculate the total travel time to reach the neighboring by traveling throught eh current station

    new_distance = current_distance + travel_time

    print(f"Current Distance: {current_distance}")
    print(f"Track Time  :{travel_time} minutes")
    print(f"New Distance: {new_distance} ")

#If the new route is shorter than the current best-known route, update our records
    if new_distance < distances[neighbor]:
        print("Shorter route found! Updating records.")
        #Update the shortest travel time
        distances[neighbor] = new_distance

        #Record the previous station so the shortest path can be reconstructed later
        previous[neighbor] = current_station

        #Add the neighboring station abck into the priority queue using its new travel time
        heapq.heappush(priority_queue, (new_distance, neighbor))
    else:
        print("Existing route is already shorter")

#show results
    print("\nFinal Distance Table")
    print("=" * 40)

    for station, distance in distances.items():
        print(f"{station} -> {distance}")

    print("\nPREVIOUS TABLE")
    print("=" * 40)

    for station, previous_station in previous.items():
        print(f"{station} -> {previous_station}")